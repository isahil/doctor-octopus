export const to_roman_numeral = (num) => {
  if (num <= 0 || num > 3999) return num.toString() // Return original number if out of range

  const roman_numerals = [
    { value: 1000, numeral: "M" },
    { value: 900, numeral: "CM" },
    { value: 500, numeral: "D" },
    { value: 400, numeral: "CD" },
    { value: 100, numeral: "C" },
    { value: 90, numeral: "XC" },
    { value: 50, numeral: "L" },
    { value: 40, numeral: "XL" },
    { value: 10, numeral: "X" },
    { value: 9, numeral: "IX" },
    { value: 5, numeral: "V" },
    { value: 4, numeral: "IV" },
    { value: 1, numeral: "I" },
  ]

  let result = ""
  for (const { value, numeral } of roman_numerals) {
    while (num >= value) {
      result += numeral
      num -= value
    }
  }

  return result
}
