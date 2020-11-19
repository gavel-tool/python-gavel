_stati = {}


def get_status(name):
    return _stati.get(name)


class Status:
    _name = None

    def __init_subclass__(cls, **kwargs):
        if cls._name:
            _stati[cls._name] = cls


class StatusSuccess(Status):
    _name = "Success"
    _abbreviation = "SUC"
    _description = "The logical data has been processed successfully."


class StatusUnsatisfiabilityPreserving(StatusSuccess):
    _name = "UnsatisfiabilityPreserving"
    _abbreviation = "UNP"
    _description = "C, i.e., if Ax is unsatisfiable then C is unsatisfiable."


class StatusSatisfiabilityPreserving(StatusSuccess):
    _name = "SatisfiabilityPreserving"
    _abbreviation = "SAP"
    _description = "- F is satisfiable."


class StatusEquiSatisfiable(
    StatusSatisfiabilityPreserving, StatusUnsatisfiabilityPreserving
):
    _name = "EquiSatisfiable"
    _abbreviation = "ESA"
    _description = "(un)satisfiable iff C is (un)satisfiable."


class StatusSatisfiable(StatusEquiSatisfiable):
    _name = "Satisfiable"
    _abbreviation = "SAT"
    _description = "- Possible dataforms are Models of Ax | C."


class StatusFinitelySatisfiable(StatusSatisfiable):
    _name = "FinitelySatisfiable"
    _abbreviation = "FSA"
    _description = "- Possible dataforms are FiniteModels of Ax | C."


class StatusFiniteTheorem(StatusSuccess):
    _name = "FiniteTheorem"
    _abbreviation = "FTH"
    _description = "- Any models of Ax | ~C are infinite."


class StatusTheorem(StatusSatisfiabilityPreserving, StatusFiniteTheorem):
    _name = "Theorem"
    _abbreviation = "THM"
    _description = "- Possible dataforms are Proofs of C from Ax."


class StatusSatisfiableTheorem(StatusTheorem):
    _name = "SatisfiableTheorem"
    _abbreviation = "STH"
    _description = "- Possible dataforms are Models of Ax with Proofs of C from Ax."


class StatusEquivalent(StatusSatisfiable, StatusSatisfiableTheorem):
    _name = "Equivalent"
    _abbreviation = "EQV"
    _description = "- Possible dataforms are Proofs of C from Ax and of Ax from C."


class StatusTautologousConclusion(StatusSatisfiable, StatusSatisfiableTheorem):
    _name = "TautologousConclusion"
    _abbreviation = "TAC"
    _description = "- Possible dataforms are Proofs of C."


class StatusWeakerConclusion(StatusSatisfiable, StatusSatisfiableTheorem):
    _name = "WeakerConclusion"
    _abbreviation = "WEC"
    _description = "- See Theorem and Satisfiable."


class StatusEquivalentTheorem(StatusEquivalent):
    _name = "EquivalentTheorem"
    _abbreviation = "ETH"
    _description = "- See Equivalent."


class StatusTautology(StatusEquivalent, StatusTautologousConclusion):
    _name = "Tautology"
    _abbreviation = "TAU"
    _description = "- Possible dataforms are Proofs of Ax and of C."


class StatusWeakerTautologousConclusion(
    StatusTautologousConclusion, StatusWeakerConclusion
):
    _name = "WeakerTautologousConclusion"
    _abbreviation = "WTC"
    _description = "- See TautologousConclusion and WeakerConclusion."


class StatusWeakerTheorem(StatusWeakerConclusion):
    _name = "WeakerTheorem"
    _abbreviation = "WTH"
    _description = "- See Theorem and Satisfiable."


class StatusCounterSatisfiabilityPreserving(StatusSuccess):
    _name = "CounterSatisfiabilityPreserving"
    _abbreviation = "CSP"
    _description = "is satisfiable then ~C is satisfiable."


class StatusCounterTheorem(StatusCounterSatisfiabilityPreserving):
    _name = "CounterTheorem"
    _abbreviation = "CTH"
    _description = "- Possible dataforms are Proofs of ~C from Ax."


class StatusContradictoryAxioms(StatusTheorem, StatusCounterTheorem):
    _name = "ContradictoryAxioms"
    _abbreviation = "CAX"
    _description = "- Possible dataforms are Refutations of Ax."


class StatusSatisfiableConclusionContradictoryAxioms(StatusContradictoryAxioms):
    _name = "SatisfiableConclusionContradictoryAxioms"
    _abbreviation = "SCA"
    _description = "- See ContradictoryAxioms."


class StatusTautologousConclusionContradictoryAxioms(
    StatusSatisfiableConclusionContradictoryAxioms
):
    _name = "TautologousConclusionContradictoryAxioms"
    _abbreviation = "TCA"
    _description = (
        "- See TautologousConclusion and SatisfiableConclusionContradictoryAxioms."
    )


class StatusSatisfiableCounterConclusionContradictoryAxioms(StatusContradictoryAxioms):
    _name = "SatisfiableCounterConclusionContradictoryAxioms"
    _abbreviation = "SCC"
    _description = "- See ContradictoryAxioms."


class StatusWeakerConclusionContradictoryAxioms(
    StatusSatisfiableConclusionContradictoryAxioms,
    StatusSatisfiableCounterConclusionContradictoryAxioms,
):
    _name = "WeakerConclusionContradictoryAxioms"
    _abbreviation = "WCA"
    _description = "SatisfiableCounterConclusionContradictoryAxioms."


class StatusCounterUnsatisfiabilityPreserving(StatusSuccess):
    _name = "CounterUnsatisfiabilityPreserving"
    _abbreviation = "CUP"
    _description = "~C, i.e., if Ax is unsatisfiable then ~C is unsatisfiable."


class StatusEquiCounterSatisfiable(
    StatusCounterUnsatisfiabilityPreserving, StatusCounterSatisfiabilityPreserving
):
    _name = "EquiCounterSatisfiable"
    _abbreviation = "ECS"
    _description = "(un)satisfiable iff ~C is (un)satisfiable."


class StatusCounterSatisfiable(StatusEquiCounterSatisfiable):
    _name = "CounterSatisfiable"
    _abbreviation = "CSA"
    _description = "- Possible dataforms are Models of Ax | ~C."


class StatusFinitelyCounterSatisfiable(StatusCounterSatisfiable):
    _name = "FinitelyCounterSatisfiable"
    _abbreviation = "FCS"
    _description = "- Possible dataforms are FiniteModels of Ax | ~C."


class StatusSatisfiableCounterTheorem(StatusCounterTheorem, StatusTheorem):
    _name = "SatisfiableCounterTheorem"
    _abbreviation = "SCT"
    _description = "- Possible dataforms are Models of Ax with Proofs of ~C from Ax."


class StatusCounterEquivalent(
    StatusSatisfiableCounterTheorem, StatusCounterSatisfiable
):
    _name = "CounterEquivalent"
    _abbreviation = "CEQ"
    _description = "- Possible dataforms are Proofs of ~C from Ax and of Ax from ~C."


class StatusUnsatisfiableConclusion(
    StatusSatisfiableCounterTheorem, StatusCounterSatisfiable
):
    _name = "UnsatisfiableConclusion"
    _abbreviation = "UNC"
    _description = "- Possible dataforms are Proofs of ~C."


class StatusWeakerCounterConclusion(
    StatusSatisfiableCounterTheorem, StatusCounterSatisfiable
):
    _name = "WeakerCounterConclusion"
    _abbreviation = "WCC"
    _description = "- See CounterTheorem and CounterSatisfiable."


class StatusFinitelyUnsatisfiable(Status):
    _name = "FinitelyUnsatisfiable"
    _abbreviation = "FUN"
    _description = "(i.e., no finite interpretations are finite models of C)."


class StatusEquivalentCounterTheorem(
    StatusCounterEquivalent, StatusFinitelyUnsatisfiable
):
    _name = "EquivalentCounterTheorem"
    _abbreviation = "ECT"
    _description = "- See CounterEquivalent."


class StatusUnsatisfiable(
    StatusFinitelyUnsatisfiable, StatusCounterEquivalent, StatusUnsatisfiableConclusion
):
    _name = "Unsatisfiable"
    _abbreviation = "UNS"
    _description = (
        "- Possible dataforms are Proofs of Ax and of C, and Refutations of F."
    )


class StatusWeakerUnsatisfiableConclusion(
    StatusWeakerCounterConclusion, StatusUnsatisfiableConclusion
):
    _name = "WeakerUnsatisfiableConclusion"
    _abbreviation = "WUC"
    _description = "- See Unsatisfiable and WeakerCounterConclusion."


class StatusWeakerCounterTheorem(StatusWeakerCounterConclusion):
    _name = "WeakerCounterTheorem"
    _abbreviation = "WCT"
    _description = "- See CounterSatisfiable."


class StatusUnsatisfiableConclusionContradictoryAxioms(
    StatusSatisfiableCounterConclusionContradictoryAxioms
):
    _name = "UnsatisfiableConclusionContradictoryAxioms"
    _abbreviation = "UCA"
    _description = "- SatisfiableCounterConclusionContradictoryAxioms."


class StatusNoConsequence(StatusSatisfiable, StatusCounterSatisfiable):
    _name = "NoConsequence"
    _abbreviation = "NOC"
    _description = "of Ax | ~C."


class StatusNoSuccess(Status):
    _name = "NoSuccess"
    _abbreviation = "NOS"
    _description = "The logical data has not been processed successfully (yet)."


class StatusOpen(StatusNoSuccess):
    _name = "Open"
    _abbreviation = "OPN"
    _description = "A success value has never been established."


class StatusUnknown(StatusNoSuccess):
    _name = "Unknown"
    _abbreviation = "UNK"
    _description = "Success value unknown, and no assumption has been made."


class StatusStopped(StatusUnknown):
    _name = "Stopped"
    _abbreviation = "STP"
    _description = (
        "Software attempted to process the data, and stopped without a success status."
    )


class StatusError(StatusStopped):
    _name = "Error"
    _abbreviation = "ERR"
    _description = "Software stopped due to an error."


class StatusOSError(StatusError):
    _name = "OSError"
    _abbreviation = "OSE"
    _description = "Software stopped due to an operating system error."


class StatusInputError(StatusError):
    _name = "InputError"
    _abbreviation = "INE"
    _description = "Software stopped due to an input error."


class StatusUsageError(StatusInputError):
    _name = "UsageError"
    _abbreviation = "USE"
    _description = "Software stopped due to an ATP system usage error."


class StatusSyntaxError(StatusInputError):
    _name = "SyntaxError"
    _abbreviation = "SYE"
    _description = "Software stopped due to an input syntax error."


class StatusSemanticError(StatusInputError):
    _name = "SemanticError"
    _abbreviation = "SEE"
    _description = "Software stopped due to an input semantic error."


class StatusTypeError(StatusSemanticError):
    _name = "TypeError"
    _abbreviation = "TYE"
    _description = (
        "Software stopped due to an input type error (for typed logical data)."
    )


class StatusForced(StatusStopped):
    _name = "Forced"
    _abbreviation = "FOR"
    _description = "Software was forced to stop by an external force."


class StatusUser(StatusForced):
    _name = "User"
    _abbreviation = "USR"
    _description = "Software was forced to stop by the user."


class StatusGaveUp(StatusStopped):
    _name = "GaveUp"
    _abbreviation = "GUP"
    _description = "Software gave up of its own accord."


class StatusResourceOut(StatusForced, StatusGaveUp):
    _name = "ResourceOut"
    _abbreviation = "RSO"
    _description = "Software stopped because some resource ran out."


class StatusTimeout(StatusResourceOut):
    _name = "Timeout"
    _abbreviation = "TMO"
    _description = "Software stopped because the CPU time limit ran out."


class StatusMemoryOut(StatusResourceOut):
    _name = "MemoryOut"
    _abbreviation = "MMO"
    _description = "Software stopped because the memory limit ran out."


class StatusIncomplete(StatusGaveUp):
    _name = "Incomplete"
    _abbreviation = "INC"
    _description = "Software gave up because it's incomplete."


class StatusNotTried(StatusUnknown):
    _name = "NotTried"
    _abbreviation = "NTT"
    _description = "Software has not tried to process the data."


class StatusInappropriate(StatusGaveUp, StatusNotTried):
    _name = "Inappropriate"
    _abbreviation = "IAP"
    _description = "Software gave up because it cannot process this type of data."


class StatusInProgress(StatusUnknown):
    _name = "InProgress"
    _abbreviation = "INP"
    _description = "Software is still running."


class StatusNotTriedYet(StatusNotTried):
    _name = "NotTriedYet"
    _abbreviation = "NTY"
    _description = (
        "Software has not tried to process the data yet, but might in the future."
    )
