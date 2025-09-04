#!/bin/bash
# 🔄 Flyde Flow Execution Script
# Execute any Flyde flow with input data and output capture

FLOW_FILE=${1:-"flows/hello-world.flyde"}
INPUT_DATA=${2:-'{"message": "Hello from script!"}'}
OUTPUT_FILE=${3:-"output.json"}

echo "🔄 Executing Flow: $FLOW_FILE"
echo "📥 Input: $INPUT_DATA"
echo "📤 Output: $OUTPUT_FILE"

# Run flow with input and save output
npx flyde run $FLOW_FILE --input "$INPUT_DATA" --output $OUTPUT_FILE

echo "✅ Flow execution complete!"
echo "📄 Results saved to: $OUTPUT_FILE"
