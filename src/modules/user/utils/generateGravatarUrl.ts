/**
 * Generates a Gravatar URL from an email address.
 * Gravatar URLs use MD5 hash of the email (lowercased and trimmed).
 */

/**
 * Simple MD5 implementation for generating Gravatar hashes
 * Based on a lightweight MD5 implementation
 */
function md5(string: string): string {
  function md5cycle(x: number[], k: number[]): void {
    let a = x[0]!
    let b = x[1]!
    let c = x[2]!
    let d = x[3]!

    a = ff(a, b, c, d, k[0] ?? 0, 7, -680876936)
    d = ff(d, a, b, c, k[1] ?? 0, 12, -389564586)
    c = ff(c, d, a, b, k[2] ?? 0, 17, 606105819)
    b = ff(b, c, d, a, k[3] ?? 0, 22, -1044525330)
    a = ff(a, b, c, d, k[4] ?? 0, 7, -176418897)
    d = ff(d, a, b, c, k[5] ?? 0, 12, 1200080426)
    c = ff(c, d, a, b, k[6] ?? 0, 17, -1473231341)
    b = ff(b, c, d, a, k[7] ?? 0, 22, -45705983)
    a = ff(a, b, c, d, k[8] ?? 0, 7, 1770035416)
    d = ff(d, a, b, c, k[9] ?? 0, 12, -1958414417)
    c = ff(c, d, a, b, k[10] ?? 0, 17, -42063)
    b = ff(b, c, d, a, k[11] ?? 0, 22, -1990404162)
    a = ff(a, b, c, d, k[12] ?? 0, 7, 1804603682)
    d = ff(d, a, b, c, k[13] ?? 0, 12, -40341101)
    c = ff(c, d, a, b, k[14] ?? 0, 17, -1502002290)
    b = ff(b, c, d, a, k[15] ?? 0, 22, 1236535329)

    a = gg(a, b, c, d, k[1] ?? 0, 5, -165796510)
    d = gg(d, a, b, c, k[6] ?? 0, 9, -1069501632)
    c = gg(c, d, a, b, k[11] ?? 0, 14, 643717713)
    b = gg(b, c, d, a, k[0] ?? 0, 20, -373897302)
    a = gg(a, b, c, d, k[5] ?? 0, 5, -701558691)
    d = gg(d, a, b, c, k[10] ?? 0, 9, 38016083)
    c = gg(c, d, a, b, k[15] ?? 0, 14, -660478335)
    b = gg(b, c, d, a, k[4] ?? 0, 20, -405537848)
    a = gg(a, b, c, d, k[9] ?? 0, 5, 568446438)
    d = gg(d, a, b, c, k[14] ?? 0, 9, -1019803690)
    c = gg(c, d, a, b, k[3] ?? 0, 14, -187363961)
    b = gg(b, c, d, a, k[8] ?? 0, 20, 1163531501)
    a = gg(a, b, c, d, k[13] ?? 0, 5, -1444681467)
    d = gg(d, a, b, c, k[2] ?? 0, 9, -51403784)
    c = gg(c, d, a, b, k[7] ?? 0, 14, 1735328473)
    b = gg(b, c, d, a, k[12] ?? 0, 20, -1926607734)

    a = hh(a, b, c, d, k[5] ?? 0, 4, -378558)
    d = hh(d, a, b, c, k[8] ?? 0, 11, -2022574463)
    c = hh(c, d, a, b, k[11] ?? 0, 16, 1839030562)
    b = hh(b, c, d, a, k[14] ?? 0, 23, -35309556)
    a = hh(a, b, c, d, k[1] ?? 0, 4, -1530992060)
    d = hh(d, a, b, c, k[4] ?? 0, 11, 1272893353)
    c = hh(c, d, a, b, k[7] ?? 0, 16, -155497632)
    b = hh(b, c, d, a, k[10] ?? 0, 23, -1094730640)
    a = hh(a, b, c, d, k[13] ?? 0, 4, 681279174)
    d = hh(d, a, b, c, k[0] ?? 0, 11, -358537222)
    c = hh(c, d, a, b, k[3] ?? 0, 16, -722521979)
    b = hh(b, c, d, a, k[6] ?? 0, 23, 76029189)
    a = hh(a, b, c, d, k[9] ?? 0, 4, -640364487)
    d = hh(d, a, b, c, k[12] ?? 0, 11, -421815835)
    c = hh(c, d, a, b, k[15] ?? 0, 16, 530742520)
    b = hh(b, c, d, a, k[2] ?? 0, 23, -995338651)

    a = ii(a, b, c, d, k[0] ?? 0, 6, -198630844)
    d = ii(d, a, b, c, k[7] ?? 0, 10, 1126891415)
    c = ii(c, d, a, b, k[14] ?? 0, 15, -1416354905)
    b = ii(b, c, d, a, k[5] ?? 0, 21, -57434055)
    a = ii(a, b, c, d, k[12] ?? 0, 6, 1700485571)
    d = ii(d, a, b, c, k[3] ?? 0, 10, -1894986606)
    c = ii(c, d, a, b, k[10] ?? 0, 15, -1051523)
    b = ii(b, c, d, a, k[1] ?? 0, 21, -2054922799)
    a = ii(a, b, c, d, k[8] ?? 0, 6, 1873313359)
    d = ii(d, a, b, c, k[15] ?? 0, 10, -30611744)
    c = ii(c, d, a, b, k[6] ?? 0, 15, -1560198380)
    b = ii(b, c, d, a, k[13] ?? 0, 21, 1309151649)
    a = ii(a, b, c, d, k[4] ?? 0, 6, -145523070)
    d = ii(d, a, b, c, k[11] ?? 0, 10, -1120210379)
    c = ii(c, d, a, b, k[2] ?? 0, 15, 718787259)
    b = ii(b, c, d, a, k[9] ?? 0, 21, -343485551)

    x[0] = add32(a, x[0]!)
    x[1] = add32(b, x[1]!)
    x[2] = add32(c, x[2]!)
    x[3] = add32(d, x[3]!)
  }

  function cmn(q: number, a: number, b: number, x: number, s: number, t: number): number {
    a = add32(add32(a, q), add32(x, t))
    return add32((a << s) | (a >>> (32 - s)), b)
  }

  function ff(a: number, b: number, c: number, d: number, x: number, s: number, t: number): number {
    return cmn((b & c) | (~b & d), a, b, x, s, t)
  }

  function gg(a: number, b: number, c: number, d: number, x: number, s: number, t: number): number {
    return cmn((b & d) | (c & ~d), a, b, x, s, t)
  }

  function hh(a: number, b: number, c: number, d: number, x: number, s: number, t: number): number {
    return cmn(b ^ c ^ d, a, b, x, s, t)
  }

  function ii(a: number, b: number, c: number, d: number, x: number, s: number, t: number): number {
    return cmn(c ^ (b | ~d), a, b, x, s, t)
  }

  function add32(a: number, b: number): number {
    return (a + b) & 0xFFFFFFFF
  }

  function rhex(n: number): string {
    const hexChars = '0123456789abcdef'
    let s = ''
    for (let j = 0; j < 4; j++) {
      s += hexChars.charAt((n >> (j * 8 + 4)) & 0x0F) + hexChars.charAt((n >> (j * 8)) & 0x0F)
    }
    return s
  }

  const utf8Encode = (str: string): string => {
    str = str.replace(/\r\n/g, '\n')
    let utftext = ''
    for (let n = 0; n < str.length; n++) {
      const c = str.charCodeAt(n)
      if (c < 128) {
        utftext += String.fromCharCode(c)
      } else if ((c > 127) && (c < 2048)) {
        utftext += String.fromCharCode((c >> 6) | 192)
        utftext += String.fromCharCode((c & 63) | 128)
      } else {
        utftext += String.fromCharCode((c >> 12) | 224)
        utftext += String.fromCharCode(((c >> 6) & 63) | 128)
        utftext += String.fromCharCode((c & 63) | 128)
      }
    }
    return utftext
  }

  const x: number[] = []
  let k: number[] = []
  let aa: number, bb: number, cc: number, dd: number
  let i: number

  const str = utf8Encode(string)
  const strLen = str.length

  x[0] = 1732584193
  x[1] = -271733879
  x[2] = -1732584194
  x[3] = 271733878

  for (i = 0; i + 64 <= strLen; i += 64) {
    k = [
      str.charCodeAt(i) | (str.charCodeAt(i + 1) << 8) | (str.charCodeAt(i + 2) << 16) | (str.charCodeAt(i + 3) << 24),
      str.charCodeAt(i + 4) | (str.charCodeAt(i + 5) << 8) | (str.charCodeAt(i + 6) << 16) | (str.charCodeAt(i + 7) << 24),
      str.charCodeAt(i + 8) | (str.charCodeAt(i + 9) << 8) | (str.charCodeAt(i + 10) << 16) | (str.charCodeAt(i + 11) << 24),
      str.charCodeAt(i + 12) | (str.charCodeAt(i + 13) << 8) | (str.charCodeAt(i + 14) << 16) | (str.charCodeAt(i + 15) << 24),
      str.charCodeAt(i + 16) | (str.charCodeAt(i + 17) << 8) | (str.charCodeAt(i + 18) << 16) | (str.charCodeAt(i + 19) << 24),
      str.charCodeAt(i + 20) | (str.charCodeAt(i + 21) << 8) | (str.charCodeAt(i + 22) << 16) | (str.charCodeAt(i + 23) << 24),
      str.charCodeAt(i + 24) | (str.charCodeAt(i + 25) << 8) | (str.charCodeAt(i + 26) << 16) | (str.charCodeAt(i + 27) << 24),
      str.charCodeAt(i + 28) | (str.charCodeAt(i + 29) << 8) | (str.charCodeAt(i + 30) << 16) | (str.charCodeAt(i + 31) << 24),
      str.charCodeAt(i + 32) | (str.charCodeAt(i + 33) << 8) | (str.charCodeAt(i + 34) << 16) | (str.charCodeAt(i + 35) << 24),
      str.charCodeAt(i + 36) | (str.charCodeAt(i + 37) << 8) | (str.charCodeAt(i + 38) << 16) | (str.charCodeAt(i + 39) << 24),
      str.charCodeAt(i + 40) | (str.charCodeAt(i + 41) << 8) | (str.charCodeAt(i + 42) << 16) | (str.charCodeAt(i + 43) << 24),
      str.charCodeAt(i + 44) | (str.charCodeAt(i + 45) << 8) | (str.charCodeAt(i + 46) << 16) | (str.charCodeAt(i + 47) << 24),
      str.charCodeAt(i + 48) | (str.charCodeAt(i + 49) << 8) | (str.charCodeAt(i + 50) << 16) | (str.charCodeAt(i + 51) << 24),
      str.charCodeAt(i + 52) | (str.charCodeAt(i + 53) << 8) | (str.charCodeAt(i + 54) << 16) | (str.charCodeAt(i + 55) << 24),
      str.charCodeAt(i + 56) | (str.charCodeAt(i + 57) << 8) | (str.charCodeAt(i + 58) << 16) | (str.charCodeAt(i + 59) << 24),
      str.charCodeAt(i + 60) | (str.charCodeAt(i + 61) << 8) | (str.charCodeAt(i + 62) << 16) | (str.charCodeAt(i + 63) << 24),
    ]
    md5cycle(x, k)
  }

  k = new Array(16).fill(0)
  const tail = strLen - i
  if (tail > 0) {
    for (let j = 0; j < tail; j++) {
      k[j] = str.charCodeAt(i + j)
    }
  }

  k[tail] = 0x80

  if (tail >= 14) {
    md5cycle(x, k)
    k = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  }

  k[14] = (strLen * 8) & 0xFFFFFFFF
  k[15] = ((strLen * 8) >>> 32) & 0xFFFFFFFF
  md5cycle(x, k)

  return rhex(x[0]!) + rhex(x[1]!) + rhex(x[2]!) + rhex(x[3]!)
}

/**
 * Generates a Gravatar URL from an email address.
 * @param email - The email address to generate a Gravatar URL for
 * @returns The Gravatar URL
 */
export function generateGravatarUrl(email: string): string {
  if (!email || !email.trim()) {
    throw new Error('Email is required to generate Gravatar URL')
  }

  // Gravatar requires lowercase, trimmed email
  const normalizedEmail = email.toLowerCase().trim()
  
  // Generate MD5 hash
  const hash = md5(normalizedEmail)
  
  // Return Gravatar URL
  return `https://www.gravatar.com/avatar/${hash}?d=404`
}
