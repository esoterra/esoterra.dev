// we have to know all of these properties before calling the encryption method
const hash = "SHA-256";
const salt = "e!3dAg$d#o#qhRyA";
const iterations = 1000;
const keyLength = 48;

const utf8Encoder = new TextEncoder("utf-8");
const utf8Decoder = new TextDecoder("utf-8");

async function getDerivation(hash, salt, password, iterations, keyLength) {
  const passwordBuffer = utf8Encoder.encode(password);
  const importedKey = await crypto.subtle.importKey("raw", passwordBuffer, "PBKDF2", false, ["deriveBits"]);

  const saltBuffer = utf8Encoder.encode(salt);
  const params = {name: "PBKDF2", hash: hash, salt: saltBuffer, iterations: iterations};
  const derivation = await crypto.subtle.deriveBits(params, importedKey, keyLength*8);
  return derivation;
}

async function getKey(derivation) {
  const keylen = 32;
  const derivedKey = derivation.slice(0, keylen);
  const iv = derivation.slice(keylen);
  const importedEncryptionKey = await crypto.subtle.importKey('raw', derivedKey, { name: 'AES-CBC' }, false, ['encrypt', 'decrypt']);
  return {
    key: importedEncryptionKey,
    iv: iv
  }
}

async function encrypt(text, keyObject) {
    const textBuffer = utf8Encoder.encode(text);
    const encryptedText = await crypto.subtle.encrypt({ name: 'AES-CBC', iv: keyObject.iv }, keyObject.key, textBuffer);
    return encryptedText;
}

async function decrypt(encryptedText, keyObject) {
    const decryptedText = await crypto.subtle.decrypt({ name: 'AES-CBC', iv: keyObject.iv }, keyObject.key, encryptedText);
    return utf8Decoder.decode(decryptedText);
}

async function encryptData(text, password) {
	const derivation = await getDerivation(hash, salt, password, iterations, keyLength);
	const keyObject = await getKey(derivation);
	const encryptedObject = await encrypt(text, keyObject);
	return encryptedObject;
}

async function decryptData(encryptedObject, password) {
	const derivation = await getDerivation(hash, salt, password, iterations, keyLength);
	const keyObject = await getKey(derivation);
	const decryptedObject = await decrypt(encryptedObject, keyObject);
	return decryptedObject;
}

function hexEncode(bytes) {
    const uint8Array = new Uint8Array(bytes);
    const byteStrings = Array.from(uint8Array).map(v => v.toString(16).padStart(2, '0'));
    console.log(byteStrings)
    return byteStrings.join('')
}

function hexDecode(hex) {
    return new Uint8Array([...hex.matchAll(/../g)].map(m => parseInt(m[0], 16))).buffer
}

async function setupSlipper() {
    const cypherTextElement = document.getElementById("slipper-cypher-text");
    const inputElement = document.getElementById("slipper-input");
    const outputElement = document.getElementById("slipper-output");
    console.log({cypherTextElement, inputElement, outputElement })

    const cypherTextHex = cypherTextElement.value;
    console.log(cypherTextHex)
    const cypherTextBytes = hexDecode(cypherTextHex);

    let lastValue = "";

    inputElement.addEventListener('input', (ev) => {
        let newValue = inputElement.value.toLowerCase().trim();
        if(newValue.charAt( newValue.length-1 ) == "s") {
            newValue = newValue.slice(0, -1)
        }
        if (newValue != lastValue) {
            lastValue = newValue;

            const tryDecrypt = async () => {
                try {
                    const plainTextRecovered = await decryptData(cypherTextBytes, newValue);
                    outputElement.innerText = plainTextRecovered
                } catch (e) {
                    outputElement.innerText = "Password incorrect"
                }
            }
            tryDecrypt()
        }
    })
}
setupSlipper()