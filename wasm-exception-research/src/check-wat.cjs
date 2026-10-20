const fs = require('node:fs');
const assert = require('node:assert/strict');
const bytes = fs.readFileSync(process.argv[2]);
console.log('validate:', WebAssembly.validate(bytes));
const module_ = new WebAssembly.Module(bytes);
const instance = new WebAssembly.Instance(module_);
assert.equal(instance.exports.answer(), 42);
console.log('answer=42');
