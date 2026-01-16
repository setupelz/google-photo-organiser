#!/bin/bash
# Ralph Wiggum Loop - Autonomous AI Development
# Based on methodology by Geoffrey Huntley (ghuntley.com/ralph)
#
# Usage:
#   ./loop.sh plan          # Interactive planning session (single run)
#   ./loop.sh plan 5        # Autonomous planning (5 iterations, non-interactive)
#   ./loop.sh              # Build mode, unlimited iterations
#   ./loop.sh 20           # Build mode, max 20 iterations
#
# Modes:
#   PLAN  - Interactive session with human. Claude asks questions,
#           you provide answers. Results in agreed IMPLEMENTATION_PLAN.md.
#   BUILD - Autonomous loop. Claude works through the plan, commits
#           changes, iterates until done or max iterations reached.
#
# Philosophy:
#   "Let Ralph Ralph" - Trust the LLM to self-correct through iteration.
#   Each iteration reads updated IMPLEMENTATION_PLAN.md, maintaining state
#   across fresh context windows. Tests/builds provide backpressure.

set -e

# Parse arguments
MODE="build"
PROMPT_FILE="PROMPT_build.md"
MAX_ITERATIONS=0
INTERACTIVE=false

if [ "$1" = "plan" ]; then
    MODE="plan"
    PROMPT_FILE="PROMPT_plan.md"
    # Check if iterations specified (non-interactive mode)
    if [[ "$2" =~ ^[0-9]+$ ]]; then
        MAX_ITERATIONS=$2
        INTERACTIVE=false
    else
        INTERACTIVE=true
    fi
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    MAX_ITERATIONS=$1
fi

BRANCH=$(git branch --show-current 2>/dev/null || echo "main")

# Header
echo "═══════════════════════════════════════"
echo "🤖 Ralph Wiggum - $(basename "$(pwd)")"
echo "═══════════════════════════════════════"
echo "Mode:       $MODE"
echo "Prompt:     $PROMPT_FILE"
echo "Branch:     $BRANCH"
[ "$MODE" = "build" ] && [ $MAX_ITERATIONS -gt 0 ] && echo "Max Iter:   $MAX_ITERATIONS"
echo "═══════════════════════════════════════"
echo ""

# Verify prompt exists
if [ ! -f "$PROMPT_FILE" ]; then
    echo "❌ Error: $PROMPT_FILE not found"
    echo ""
    echo "Create it with:"
    echo "  cp ../../../config/project-template/PROMPT_${MODE}_template.md $PROMPT_FILE"
    exit 1
fi

# Verify AGENTS.md exists (warning only)
if [ ! -f "AGENTS.md" ] && [ ! -f "CLAUDE.md" ]; then
    echo "⚠️  Warning: No AGENTS.md or CLAUDE.md found"
    echo "   Consider adding project-specific build/test commands"
    echo ""
fi

#######################################
# PLAN MODE: Interactive or autonomous
#######################################
if [ "$MODE" = "plan" ]; then
    if [ "$INTERACTIVE" = true ]; then
        # Interactive planning - human in the loop
        echo "📋 Starting interactive planning session..."
        echo "   Claude will ask questions to refine the plan."
        echo "   Type responses when prompted."
        echo ""

        # Run Claude interactively (NOT piped, NOT looped)
        # Uses Opus for better reasoning during planning
        claude --model opus --dangerously-skip-permissions --verbose "$(cat "$PROMPT_FILE")"

        echo ""
        echo "═══════════════════════════════════════"
        echo "📋 Planning session complete"
        echo "   Review: IMPLEMENTATION_PLAN.md"
        echo "   Next:   ./loop.sh [iterations]"
        echo "═══════════════════════════════════════"
        exit 0
    else
        # Non-interactive planning - autonomous mode
        echo "📋 Starting autonomous planning..."
        echo "   Claude will create/update the implementation plan."
        echo "   Max iterations: $MAX_ITERATIONS"
        echo ""
        # Fall through to build loop logic below, but with plan prompt
    fi
fi

#######################################
# AUTONOMOUS LOOP (build or non-interactive plan)
#######################################
if [ "$MODE" = "plan" ]; then
    echo "📋 Running autonomous planning loop..."
else
    echo "🔨 Starting autonomous build loop..."
fi
echo "   Press Ctrl+C to stop gracefully"
echo ""

ITERATION=0
PHASE_COMPLETE=false

# Prepare prompt content - inject autonomous mode header for non-interactive planning
if [ "$MODE" = "plan" ] && [ "$INTERACTIVE" = false ]; then
    PROMPT_CONTENT="AUTONOMOUS MODE - DO NOT ASK QUESTIONS

You are running in autonomous/headless mode via Telegram. There is no human to answer questions.

CRITICAL INSTRUCTIONS:
- Do NOT use AskUserQuestion - it will fail
- Do NOT ask for confirmation or clarification
- Auto-select all specs marked '🚧 In Progress' or '📋 Planned'
- Make reasonable assumptions for any ambiguity
- Document assumptions in the plan
- Just read specs → generate plan → write IMPLEMENTATION_PLAN.md → output ###PHASE_COMPLETE###

---

$(cat "$PROMPT_FILE")"
else
    PROMPT_CONTENT="$(cat "$PROMPT_FILE")"
fi

while true; do
    # Check iteration limit
    if [ $MAX_ITERATIONS -gt 0 ] && [ $ITERATION -ge $MAX_ITERATIONS ]; then
        echo ""
        echo "✅ Reached max iterations: $MAX_ITERATIONS"
        break
    fi

    # Check if phase was completed in previous iteration
    if [ "$PHASE_COMPLETE" = true ]; then
        echo ""
        echo "✅ Phase complete - Ralph finished successfully"
        break
    fi

    echo ""
    echo "══════ Iteration $((ITERATION + 1)) ══════"
    echo ""

    # Run Claude and capture output, looking for completion signal
    # Using tee to both display and capture output
    OUTPUT_FILE=$(mktemp)

    # Run Claude autonomously with piped prompt
    # -p (headless mode): non-interactive operation
    # --dangerously-skip-permissions: autonomous operation
    #   ⚠️  USE IN SANDBOX ONLY! When compromised, minimize blast radius.
    # --model sonnet: speed and cost efficiency for implementation
    echo "$PROMPT_CONTENT" | claude -p \
        --dangerously-skip-permissions \
        --model sonnet \
        --verbose 2>&1 | tee "$OUTPUT_FILE"

    EXIT_CODE=${PIPESTATUS[1]}

    # Check for phase completion signal in output
    if grep -q "###PHASE_COMPLETE###" "$OUTPUT_FILE" 2>/dev/null; then
        PHASE_COMPLETE=true
        echo ""
        echo "📍 Detected completion signal"
    fi

    # Clean up temp file
    rm -f "$OUTPUT_FILE"

    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "✓ Iteration complete"
    else
        echo ""
        echo "⚠ Iteration exited with code $EXIT_CODE"
    fi

    # Push changes after each iteration
    if git diff --quiet && git diff --cached --quiet; then
        echo "  No changes to push"
    else
        echo "  Pushing changes..."
        git push origin "$BRANCH" 2>/dev/null || \
            git push -u origin "$BRANCH" 2>/dev/null || \
            echo "  ⚠ Push failed (continuing anyway)"
    fi

    ITERATION=$((ITERATION + 1))

    # Brief pause for operator to interrupt if needed
    sleep 1
done

echo ""
echo "═══════════════════════════════════════"
echo "🎉 Ralph finished after $ITERATION iterations"
echo "═══════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  - Review: git log --oneline -10"
echo "  - Status: cat IMPLEMENTATION_PLAN.md"
echo "  - Verify: run tests/build"
echo ""
