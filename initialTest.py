import smartpy as sp

class SimpleMath(sp.Contract):
    def __init__(self):
        self.init(sum = 0)

    @sp.entryPoint
    def computeSum(self, params):
        self.data.sum = params.augend + params.addend

@addTest(name = "MathTest")
def test():
    scenario = sp.testScenario()
    scenario.h1("Simple Math Tests")

    contract = SimpleMath()

    scenario += contract
    scenario.h2("Test Addition")
    scenario += contract.computeSum(augend = 1, addend = 2).run(sender = sp.address("tz1234"))

    scenario.verify(contract.data.sum == 3)
