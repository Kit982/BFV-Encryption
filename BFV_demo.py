from BFV import *
from poly import *
from helper import *
import json
import socket


def _serializer(x):
    if isinstance(x, Poly):
        return {'n': x.n, 'q': x.q, 'np': x.np, 'F': x.F, 'inNTT': x.inNTT}
        #return x.__dict__


class TestEncoder(json.JSONEncoder):
    def default(self, o):
        return {"n": o.n, "q": o.q, "np": o.np, "F": o.F, "inNTT": o.inNTT}


def decode_(dct):
    if "__poly__" in dct:
        return Poly.__str__(dct)
    return dct


def poly_to_str(pol):
    # return str(pol)
    return {'n': pol.n, 'q': pol.q, 'np': pol.np, 'F': pol.F, 'inNTT': pol.inNTT}


def str_to_poly(str1):
    return Poly.self_i(str1)


#import json
#import socket


from random import randint
from math import log, ceil


# This implementation follows the description at https://eprint.iacr.org/2012/144.pdf
# Brakerski/Fan-Vercauteren (BFV) somewhat homomorphic encryption scheme
#
# Polynomial arithmetic on ciphertext domain is performed in Z[x]_q/x^n+1
# Polynomial arithmetic on plaintext domain is performed in Z[x]_t/x^n+1
# * n: ring size
# * q: ciphertext coefficient modulus
# * t: plaintext coefficient modulus (if t is equal to 2, no negative values is accepted)
# * psi,psiv,w,wv: polynomial arithmetic parameters
#
# Note that n,q,t parameters together determine the multiplicative depth.

# Parameter generation (pre-defined or generate parameters)
PD = 0 # 0: generate -- 1: pre-defined

if PD == 0:
    # Select one of the parameter sets below
    t = 16;   n, q, psi = 1024 , 132120577         , 73993                # log(q) = 27
    # t = 256;  n, q, psi = 2048 , 137438691329      , 22157790             # log(q) = 37
    # t = 1024; n, q, psi = 4096 , 288230376135196673, 60193018759093       # log(q) = 58

    # other necessary parameters
    psiv= modinv(psi,q)
    w   = pow(psi,2,q)
    wv  = modinv(w,q)
else:
    # Enter proper parameters below
    t, n, logq = 16, 1024, 27
    # t, n, logq = 256, 2048, 37
    # t, n, logq = 1024, 4096, 58

    # other necessary parameters (based on n and log(q) determine other parameter)
    q,psi,psiv,w,wv = ParamGen(n,logq) 

# Determine mu, sigma (for discrete gaussian distribution)
mu    = 0
sigma = 0.5 * 3.2

# Determine T, p (for relinearization and galois keys) based on noise analysis 
T = 256
p = q**3 + 1

# Generate polynomial arithmetic tables
w_table    = [1]*n
wv_table   = [1]*n
psi_table  = [1]*n
psiv_table = [1]*n
for i in range(1,n):
    w_table[i]    = ((w_table[i-1]   *w)    % q)
    wv_table[i]   = ((wv_table[i-1]  *wv)   % q)
    psi_table[i]  = ((psi_table[i-1] *psi)  % q)
    psiv_table[i] = ((psiv_table[i-1]*psiv) % q)

qnp = [w_table,wv_table,psi_table,psiv_table]

print("--- Starting BFV Demo")

# Generate BFV evaluator
Evaluator = BFV(n, q, t, mu, sigma, qnp)

# Generate Keys
Evaluator.SecretKeyGen()
Evaluator.PublicKeyGen()
Evaluator.EvalKeyGenV1(T)
Evaluator.EvalKeyGenV2(p)

# print system parameters
print(Evaluator)

# Generate random message
# n1, n2 = 15, -5
# n1, n2 = randint(-(2**15),2**15-1), randint(-(2**15),2**15-1)
n1, n2 = 145, 56

print("--- Integers n1 and n2.")
print("* n1: {}".format(n1))
print("* n2: {}".format(n2))
print("* n1+n2: {}".format(n1+n2))
print("* n1-n2: {}".format(n1-n2))
print("* n1*n2: {}".format(n1*n2))
print("")

# Encode messages into plaintext polynomials
print("--- n1 and n2 are encoded as polynomials m1(x) and m2(x).")
m1 = Evaluator.IntEncode(n1)
m2 = Evaluator.IntEncode(n2)

print("* m1(x): {}".format(m1))
print("* m2(x): {}".format(m2))
print("")

# Encrypt message
ct1 = Evaluator.Encryption(m1)
ct2 = Evaluator.Encryption(m2)

print(type(ct1))
# print(ct1[0])
print("")

ct_11 = poly_to_str(ct1[0])
ct_12 = poly_to_str(ct1[1])
ct_21 = poly_to_str(ct1[0])
ct_22 = poly_to_str(ct1[1])
# print(ct_11)

poly_11 = str_to_poly(ct_11)
poly_12 = str_to_poly(ct_12)
poly_21 = str_to_poly(ct_21)
poly_22 = str_to_poly(ct_22)

print(type(poly_12))
print("")

# print(vars(ct1[0]))
# db = Poly.toPOL(poly_11)
# print(db)

print("--- ct1 and ct2 in json.")
data = {"x": [ct_11, ct_12], "y": [ct_21, ct_22], "id": 1} #, "__poly__": 1}
json_data = json.dumps(data)#, cls=TestEncoder)#default=_serializer)
# print(json_data)
print(type(json_data))
print("")
json_info = json.loads(json_data)#, object_hook=decode_)
print(type(json_info["x"]))
print("")
#print(json_info["x"])

#xjson = Poly.__str__(json_info["x"])
#yjson = Poly.__str__(json_info["y"])

# print(json_info["x"])
print("")
# print(json_data)
# print("")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('localhost', 3030))  # Подключаемся к нашему серверу.
s.send(json_data.encode('utf-8'))  # Отправляем фразу.
data = s.recv(10000000000)  # Получаем данные из сокета.
# data = data.decode("utf-8")
s.close()

print("Received: {}".format(data))



print("--- m1 and m2 are encrypted as ct1 and ct2.")
"""print("* ct1[0]: {}".format(ct1[0]))
print("* ct1[1]: {}".format(ct1[1]))
print("* ct2[0]: {}".format(ct2[0]))
print("* ct2[1]: {}".format(ct2[1]))"""
print("")


print(type(ct1[0]))
print(type(json_info["x"]))
print("")
# Homomorphic Addition
ct = Evaluator.HomomorphicAddition(ct1, ct2)
# ct = Evaluator.HomomorphicAddition(xjson, yjson)
# ct = Evaluator.HomomorphicAddition(str(json_info["x"]), str(json_info["y"]))

print(type(ct[0]))
print("")
mt = Evaluator.Decryption(ct)

nr = Evaluator.IntDecode(mt) 
ne = (n1+n2) 

print("--- Performing ct_add = Enc(m1) + Enc(m2)")
"""print("* ct_add[0] :{}".format(ct[0]))
print("* ct_add[1] :{}".format(ct[1]))
print("--- Performing ct_dec = Dec(ct_add)")
print("* ct_dec    :{}".format(mt))"""
print("--- Performing ct_dcd = Decode(ct_dec)")
print("* ct_dcd    :{}".format(nr))

if nr == ne:
    print("* Homomorphic addition works.")
else:
    print("* Homomorphic addition does not work.")
print("")

"""
# Homomorphic Subtraction
ct = Evaluator.HomomorphicSubtraction(ct1,ct2)
mt = Evaluator.Decryption(ct)

nr = Evaluator.IntDecode(mt) 
ne = (n1-n2) 

print("--- Performing ct_sub = Enc(m1) - Enc(m2)")
print("* ct_sub[0] :{}".format(ct[0]))
print("* ct_sub[1] :{}".format(ct[1]))
print("--- Performing ct_dec = Dec(ct_sub)")
print("* ct_dec    :{}".format(mt))
print("--- Performing ct_dcd = Decode(ct_dec)")
print("* ct_dcd    :{}".format(nr))

if nr == ne:
    print("* Homomorphic subtraction works.")
else:
    print("* Homomorphic subtraction does not work.")
print("")

# Multiply two message (no relinearization)
ct = Evaluator.HomomorphicMultiplication(ct1,ct2)
mt = Evaluator.DecryptionV2(ct)

nr = Evaluator.IntDecode(mt) 
ne = (n1*n2)

print("--- Performing ct_mul = Enc(m1) * Enc(m2) (no relinearization)")
print("* ct_mul[0] :{}".format(ct[0]))
print("* ct_mul[1] :{}".format(ct[1]))
print("--- Performing ct_dec = Dec(ct_sub)")
print("* ct_dec    :{}".format(mt))
print("--- Performing ct_dcd = Decode(ct_dec)")
print("* ct_dcd    :{}".format(nr))

if nr == ne:
    print("* Homomorphic multiplication works.")
else:
    print("* Homomorphic multiplication does not work.")
print("")

# Multiply two message (relinearization v1)
ct = Evaluator.HomomorphicMultiplication(ct1,ct2)
ct = Evaluator.RelinearizationV1(ct)
mt = Evaluator.Decryption(ct)

nr = Evaluator.IntDecode(mt)
ne = (n1*n2)

print("--- Performing ct_mul = Enc(m1) * Enc(m2) (with relinearization v1)")
print("* ct_mul[0] :{}".format(ct[0]))
print("* ct_mul[1] :{}".format(ct[1]))
print("--- Performing ct_dec = Dec(ct_sub)")
print("* ct_dec    :{}".format(mt))
print("--- Performing ct_dcd = Decode(ct_dec)")
print("* ct_dcd    :{}".format(nr))

if nr == ne:
    print("* Homomorphic multiplication works.")
else:
    print("* Homomorphic multiplication does not work.")
print("")
"""

"""
# Multiply two message (relinearization v2)
ct = Evaluator.HomomorphicMultiplication(ct1,ct2)
ct = Evaluator.RelinearizationV2(ct)
mt = Evaluator.Decryption(ct)

nr = Evaluator.IntDecode(mt)
ne = (n1*n2)

print("--- Performing ct_mul = Enc(m1) * Enc(m2) (with relinearization v2)")
print("* ct_mul[0] :{}".format(ct[0]))
print("* ct_mul[1] :{}".format(ct[1]))
print("--- Performing ct_dec = Dec(ct_sub)")
print("* ct_dec    :{}".format(mt))
print("--- Performing ct_dcd = Decode(ct_dec)")
print("* ct_dcd    :{}".format(nr))

if nr == ne:
    print("* Homomorphic multiplication works.")
else:
    print("* Homomorphic multiplication does not work.")
"""
#
