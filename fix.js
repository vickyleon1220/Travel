const fs = require('fs');
const path = 'index.html';

let content = fs.readFileSync(path, 'utf8');

// 1. Update seats for f1
// We'll find the defaultFlights array and replace the seats of the first element.
// We'll do a regex that matches the seats block for f1.
// Since the file is not too big, we can do a simple replacement for the known pattern.
// We'll replace from "seats: {" up to the closing "}" after Honn: '4A' for the first occurrence.
// We'll use a regex with the DOTALL flag to match across lines.
const seatsRegex = /(id: 'f1'[\s\S]*?seats: \{)[\s\S]*?(\})/;
// Replace with new seats
const newSeats = `        seats: {
          James: '34H',
          Vicky: '33H',
          Chenn: '33K',
          Honn: '34K'
        }`;
content = content.replace(seatsRegex, '$1' + newSeats.substring(10) + '$2');
// Wait, the above is messy. Let's do a more straightforward approach: replace the whole block we matched with the new block.
// Actually we want to keep the prefix up to the opening brace and then insert our new content and then the closing brace.
// Let's do:
//   content = content.replace(seatsRegex, (match, p1, p2) => p1 + '\n          James: \'34H\',\n          Vicky: \'33H\',\n          Chenn: \'33K\',\n          Honn: \'34K'\n        }' + p2);
// But note that p1 already includes the opening brace and the newline and spaces? Let's examine.
// We'll instead do a more precise replacement: we know the exact lines we want to replace.
// Let's do line-by-line for safety.

