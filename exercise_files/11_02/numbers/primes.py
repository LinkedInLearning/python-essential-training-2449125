from factors import getFactors 

# def isPrime(n, foundPrimes=None):
#     foundPrimes = range(2, int(n**0.5)) if foundPrimes is None else foundPrimes
#     for factor in foundPrimes:
#         if n % factor == 0:
#             return False
#     return True

def isPrime(n, foundPrimes=None):
    return len(getFactors(n)) == 2

def listPrimes(max):
    foundPrimes = []
    for n in range(2, max):
        if isPrime(n, foundPrimes):
            foundPrimes.append(n)
    return foundPrimes
    
