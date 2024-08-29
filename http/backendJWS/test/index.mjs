import { KJUR, KEYUTIL } from 'jsrsasign';

const token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoiSGVsbG8sIHdvcmxkISIsImV4cCI6MTcxODQ3NTk0Nn0.IXZKYguR1oiG5YPgnyLOZaFhExUhMzUqh8VvGztx_1chNU3gLpYkYS9s7C0OB5hcyGns3xJ67ROmnalVNzZ8j7zaLTs9JR3LWL8n7wtgC8YvfUJY0vMFWgE0Vzd3RvfqCDi8honjI_TEh2a-l9AMVumjg4NghLu3IFk4mDDpgjuQ9p9CxVYpWD5pxl6uM6sc4-grPF1tB7riC8ZmYIIKkpCzv2wX2873ASn_kESj7dFHPnkCvr4F0MAcz_xRoBpfZbTFCFO7aFVGKWWquk1wglZ0ot9jW7S6yrXgewTKAvwGKhM20JEevD9XJ3FM05Hy7NVEr27DWSNWmuOX82rb0g";

//Prefix and suffix removed
const publicKey = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAt9R5aV2vsAdn0hEiAIXc
CuhzHElfz4+jKkR+QyBAipyUcNZCCVpwJ/bSQP9tK3obcCRuUfPuTeyYyhQ+k05f
HIpZUoqfwFv0WestIVseiABh+xGrsyTDho/nnmJv4NuCI3wZwy7WLo4biaAcVYFO
E0r2dEsGEomCiQOBmJp956u06z6Sx/Q7qdNT3Z6/5Vk3ztUx1larPdZGlQR61BlL
eBRT5/q2t9/HxT/quzo9/oVmfhjmdoMAIvac+cYFfXSgi5Sacfed30P0dK5t6JW7
UoEhuy0Vj9GzxV1ZX4eNPwFxopfDtDE+WUw/zwfxkYST51yZa2wsYP6LIqWBkkTs
ewIDAQAB
-----END PUBLIC KEY-----`;

function verifyJWT(token, pubKey) {
  try {
    // Split the token into its parts
    const [headerB64, payloadB64, signatureB64] = token.split('.');

    let jws = new KJUR.jws.JWS();
    let result = 0;

    result = KJUR.jws.JWS.verify( token, pubKey, ["RS256"]);
	  return result;
  } catch (error) {
    console.error('Failed to verify JWT:', error);
    return null;
  }
}

async function main() {
var pubKey = KEYUTIL.getKey(publicKey);
    try {
 	const url = `https://happy-islands-own.loca.lt/api`
	fetch(url, 
		{ mode: 'cors', headers: { 'Access-Control-Allow-Origin':'*' } }
		  ).then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok ' + response.statusText);
		}
		return response.json();
	}).then(data => {
		console.log( data );
		const decodedPayload = verifyJWT(data, pubKey);
		console.log(decodedPayload);
	}).catch(error => {
		console.error('There was a problem with the fetch operation:', error);
	});

    } catch (error) {
        console.error(error.message);
    }
}

main();

