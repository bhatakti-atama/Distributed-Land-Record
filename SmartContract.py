
import smartpy as sp

class LandRecord(sp.Contract):
    def __init__(self, owner, govt_offcial, hashedSecret, old_owner, counterparty):
        self.init(owner     = owner,
                  hashedSecret = hashedSecret,
                  govt_offcial = govt_offcial,
                  old_owner        = old_owner,
                  counterparty = counterparty)

    def checkAlive(self, identity):
        sp.verify(self.data.notional != sp.mutez(0))
        sp.verify(identity == sp.sender)

    def finish(self):
        self.data.notional = sp.mutez(0)

    @sp.entry_point
    def allSigned(self, params):
        self.checkAlive(self.data.owner)
        sp.send(self.data.counterparty, self.data.notional)
        self.finish()

    @sp.entry_point
    def cancelSwap(self, params):
        self.checkAlive(self.data.owner)
        sp.verify(self.data.epoch < sp.now)
        sp.send(self.data.owner, self.data.notional)
        self.finish()

    @sp.entry_point
    def knownSecret(self, params):
        self.checkAlive(self.data.counterparty)
        sp.verify(self.data.hashedSecret == sp.blake2b(params.secret))
        sp.send(self.data.counterparty, self.data.notional)
        self.finish()

@sp.add_test(name = "Add New Record")
def test():
    hashSecret = sp.blake2b(sp.bytes("0x12345678aabb"))
    alice = sp.test_account("Alice")
    bob   = sp.test_account("Robert")
    c1 = LandRecord(sp.mutez(12), sp.timestamp(50), hashSecret,
                    alice.address,
                    bob.address)
    scenario  = sp.test_scenario()
    scenario.h1("Atomic Swap")
    scenario += c1

@sp.add_test(name = "CheckRecord")
def test():
    alice = sp.test_account("Alice")
    bob   = sp.test_account("Robert")
    scenario = sp.test_scenario()
    scenario.h1("Land Record")

    hashSecret = sp.blake2b(sp.bytes("0x12345678aabb"))
    c1 = AtomicSwap(sp.mutez(12), sp.timestamp(50), hashSecret,
                    alice.address,
                    bob.address)
    c2 = AtomicSwap(sp.mutez(20), sp.timestamp(50), hashSecret,
                    bob.address,
                    alice.address)
    scenario.h1("c1")
    c1.set_initial_balance(sp.tez(3))
    scenario += c1
    scenario += c1.knownSecret(secret = sp.bytes("0x12345678aa")).run(sender = bob, valid = False)
    scenario += c1.knownSecret(secret = sp.bytes("0x12345678aabb")).run(sender = bob)
    scenario.h1("c2")
    scenario += c2
    scenario.h2("C2.export()")
    scenario.p(c2.export())
