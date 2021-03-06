# -*- coding: utf-8 -*-

"""Analysis module."""

import sys

from tap.tracker import Tracker

from .enums import ResultCode
from .logging import Logger
from .printing import PrintableNameMixin, PrintableResultMixin

logger = Logger.get_logger(__name__)


class Analysis:
    """
    Analysis class.

    An instance of Analysis contains a Config object.
    Providers are first run to generate the data, then
    these data are all checked against every checker.
    """

    def __init__(self, config):
        """
        Initialization method.

        Args:
            config (Config): the configuration object to use for analysis.
        """
        self.config = config
        self.results = []

    @staticmethod
    def _get_checker_result(group, checker, provider=None, nd=""):
        logger.info("Run %schecker %s", nd, checker.identifier or checker.name)
        checker.run(provider.data if provider else None)
        return Result(group, provider, checker, *checker.result)

    def run(self, verbose=True):
        """
        Run the analysis.

        Generate data from each provider, then check these data with every
        checker, and store the analysis results.

        Args:
            verbose (bool): whether to immediately print the results or not.
        """
        self.results.clear()

        for analysis_group in self.config.analysis_groups:
            if analysis_group.providers:
                for provider in analysis_group.providers:
                    logger.info("Run provider %s", provider.identifier)
                    provider.run()
                    for checker in analysis_group.checkers:
                        result = self._get_checker_result(analysis_group, checker, provider)
                        self.results.append(result)
                        analysis_group.results.append(result)
                        if verbose:
                            result.print()
            else:
                for checker in analysis_group.checkers:
                    result = self._get_checker_result(analysis_group, checker, nd="no-data-")
                    self.results.append(result)
                    analysis_group.results.append(result)
                    if verbose:
                        result.print()

    def print_results(self):
        """Print analysis results as text on standard output."""
        for result in self.results:
            result.print()

    def output_tap(self):
        """Output analysis results in TAP format."""
        tracker = Tracker(streaming=True, stream=sys.stdout)
        for group in self.config.analysis_groups:
            n_providers = len(group.providers)
            n_checkers = len(group.checkers)
            if not group.providers and group.checkers:
                test_suite = group.name
                description_lambda = lambda r: r.checker.name
            elif not group.checkers:
                logger.warning("Invalid analysis group (no checkers), skipping")
                continue
            elif n_providers > n_checkers:
                test_suite = group.checkers[0].name
                description_lambda = lambda r: r.provider.name
            else:
                test_suite = group.providers[0].name
                description_lambda = lambda r: r.checker.name

            for result in group.results:
                description = description_lambda(result)
                if result.code == ResultCode.PASSED:
                    tracker.add_ok(test_suite, description)
                elif result.code == ResultCode.IGNORED:
                    tracker.add_ok(test_suite, description + " (ALLOWED FAILURE)")
                elif result.code == ResultCode.NOT_IMPLEMENTED:
                    tracker.add_not_ok(test_suite, description, "TODO implement the test")
                elif result.code == ResultCode.FAILED:
                    tracker.add_not_ok(
                        test_suite,
                        description,
                        diagnostics="  ---\n  message: %s\n  hint: %s\n  ..."
                        % ("\n  message: ".join(result.messages.split("\n")), result.checker.hint),
                    )

    def output_json(self):
        """Output analysis results in JSON format."""

    @property
    def successful(self):
        """Property to tell if the run was successful: no failures."""
        for result in self.results:
            if result.code == ResultCode.FAILED:
                return False
        return True


class AnalysisGroup(PrintableNameMixin):
    """Placeholder for groups of providers and checkers."""

    def __init__(self, name=None, description=None, providers=None, checkers=None):
        """
        Initialization method.

        Args:
            name (str): the group name.
            description (str): the group description.
            providers (list): the list of providers.
            checkers (list): the list of checkers.
        """
        self.name = name
        self.description = description
        self.providers = providers or []
        self.checkers = checkers or []
        self.results = []


class Result(PrintableResultMixin):
    """Placeholder for analysis results."""

    def __init__(self, group, provider, checker, code, messages):
        """
        Initialization method.

        Args:
            group (AnalysisGroup): parent group.
            provider (Provider): parent Provider.
            checker (Checker): parent Checker.
            code (int): constant from Checker class.
            messages (str): messages string.
        """
        self.group = group
        self.provider = provider
        self.checker = checker
        self.code = code
        self.messages = messages
