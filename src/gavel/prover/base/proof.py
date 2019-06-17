from gavel.dialects.db.structures import Problem


class ProverInterface:
    def prove(self, problem: Problem, *args, **kwargs):
        """
        Attempt to prove a problem specified in `file`
        :param file:
        :return:
        """
