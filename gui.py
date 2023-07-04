# Copyright 2023 Phillip Keldenich (TU Braunschweig); Sebastian Wild (University of Liverpool)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the “Software”), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software 
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import threading
import statistics
import config
import display_config
import os
import math
import games_and_strategies
import numpy as np
import traceback
import platform
import implementation
import safedirep
from copy import deepcopy

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

# Make matplotlib run through ssh session without X
import matplotlib as mpl

if display_config.completelyDisableGUI:
    mpl.use("Agg")
if display_config.gui_backend:
    mpl.use(display_config.gui_backend)


import matplotlib.pylab as plt
import matplotlib.colors as colors

# Our imports
from games_and_strategies import strategyName, morals
from misc_globals import (
    occurringStrategiesNames,
    occurringStrategies,
    numberOfDigitsInM,
    strategies,
    reputation,
    N,
    M,
    occurringInterestingMorals,
    occurringMorals,
)
from statistics import (
    reputationStats,
    perMoralMean,
    perMoralStdevAbove,
    perMoralStdevBelow,
    welfareStats,
    current,
)

plotUpdateInterval = 60  # how often the update routine runs
border = 0.05
hsep = 0.035
vsep = 0.05

numberOfOccurringStrategies = len(occurringStrategiesNames)


def reputation_diff_matrix(moral1, moral2):
    return 7 * reputation[moral1] + 3 * reputation[moral2]


def _after(arg):
    arg.updateUI()


class PlotData:
    def __init__(self, iteration):
        self.iteration = iteration
        self.reputation = None
        self.statistics = None

    def status(self):
        return (
            "Iteration "
            + str(self.iteration)
            + " of "
            + str(M)
            + " ("
            + ("%f" % (100.0 * self.iteration / M))
            + "%)"
        )

    def title(self):
        return "RepEvol Simulator - " + self.status()

    def reputation_diff_matrix(self, moral1, moral2):
        return 7 * self.reputation[moral1] + 3 * self.reputation[moral2]

    def strategy_counts(self):
        result = np.zeros(len(occurringStrategiesNames))
        index = 0
        for strategy in occurringStrategiesNames.keys():
            result[index] = self.statistics[strategy][statistics.numberOfPlayers]
            index += 1
        return result


class PlotUI:
    def __init__(self):
        # Whether we are done - needed in case the window is closed before the simulation finished
        self.done = False

        # Thread that runs the simulation
        self.thread = None
        self.queue = Queue(
            maxsize=50
        )  # if the UI threads can't keep up, at some point we have to wait.

        # Whether we have to store any images (typically, PNG files)
        self.haveImageThread = (
            not display_config.completelyDisableGUI
        ) and display_config.storeMatrices

        # If we store images in GUI mode, we do it in a separate thread
        # (except whole pictures, because they need the plot they must be rendered in the GUI thread)
        if self.haveImageThread:
            self.imagethread = threading.Thread(
                target=lambda: self._plotImagesMain(), name="imageFilePlotter"
            )
            self.imagequeue = Queue(maxsize=50)
        else:
            self.imagethread = None
            self.imagequeue = None

        # Our plot object (for the gui)
        self.plot = plt.figure(
            num=1,
            figsize=(
                display_config.sizeOfMainWindow[0] / display_config.displayDPI,
                display_config.sizeOfMainWindow[1] / display_config.displayDPI,
            ),
            dpi=display_config.displayDPI,
        )

        try:
            self.plot.canvas.set_window_title("RepEvol Simulator")
        except:
            pass
        self.initializeUI()

    def _compute_layout(self):
        self.rows = 1

        # depending on what we are showing in the first row, we need a varying number of columns
        if display_config.showInFirstRow in [
            display_config.matrices,
            display_config.matricesWithRepDiff,
        ]:
            self.columns = 2

            if config.welfareStatistics:
                self.columns += 1

            if morals.safedirep in occurringMorals:
                self.columns += 1
        elif display_config.showInFirstRow == display_config.perStrategyDetailedStats:
            self.columns = numberOfOccurringStrategies

        # ensure enough columns for second row
        if display_config.showStatsInSecondRow:
            if self.columns < 2:
                self.columns = 2
            self.rows = 2

        self.width = (1 - 2 * border - (self.columns - 1) * hsep) / self.columns
        self.height = (1 - 2 * border - (self.rows - 1) * vsep) / self.rows

    def _initialize_first_row(self):
        # get the minimal and maximal value of strategy
        minStrategyValue = min(strategyName.keys()) - 0.5
        maxStrategyValue = max(strategyName.keys()) + 0.5

        # initialize coordinates/sizes
        left = border
        bottom = 1.0 - border - self.height
        width = self.width
        height = self.height

        self.strategyRepHistPlot = {}
        if display_config.showInFirstRow in [
            display_config.matrices,
            display_config.matricesWithRepDiff,
        ]:
            # the strategies themselves
            self.strategiesPlot = plt.axes([left, bottom, width, height])
            self.strategiesPlot.set_title("Strategies")
            self.strategiesImage = plt.imshow(
                strategies,
                vmin=minStrategyValue,
                vmax=maxStrategyValue,
                interpolation="nearest",
                cmap=self.strategyColorMapDiscrete,
            )
            self.strategiesColorbar = plt.colorbar(
                self.strategiesImage,
                orientation="horizontal",
                ticks=sorted(strategyName.keys()),
            )
            self.strategiesColorbar.ax.set_xticklabels(
                self.strategyLabelsWithBlanks, rotation=90
            )
            left += width + hsep

            # reputation matrix
            if display_config.showInFirstRow == display_config.matrices:
                self.reputationPlot = plt.axes(
                    [left, bottom, width, height],
                    sharex=self.strategiesPlot,
                    sharey=self.strategiesPlot,
                )
                self.reputationPlot.set_title("Reputation")
                self.reputationImage = plt.imshow(
                    reputation[display_config.guiMoral],
                    vmin=0,
                    vmax=1,
                    interpolation="nearest",
                    cmap="hot",
                )
                self.reputationColorbar = plt.colorbar(
                    self.reputationImage, ticks=[0, 0.5, 1], orientation="horizontal"
                )
                self.reputationColorbar.ax.set_xticklabels(
                    ["0 (evil)", "0.5", "1 (good)"], rotation=45
                )
                left += width + hsep

            # reputation difference matrix
            elif display_config.showInFirstRow == display_config.matricesWithRepDiff:
                self.reputationPlot = plt.axes(
                    [left, bottom, width, height],
                    sharex=self.strategiesPlot,
                    sharey=self.strategiesPlot,
                )
                self.reputationPlot.set_title("Reputation (Diff)")
                self.reputationImage = plt.imshow(
                    reputation_diff_matrix(config.diffMorals[0], config.diffMorals[1]),
                    vmin=0,
                    vmax=10,
                    interpolation="nearest",
                    cmap=self.diffColorMap,
                )
                self.reputationColorbar = plt.colorbar(
                    self.reputationImage, ticks=[0, 3, 7, 10], orientation="horizontal"
                )
                self.reputationColorbar.ax.set_xticklabels(["BB", "BG", "GB", "GG"])
                left += width + hsep

            # welfare
            if config.welfareStatistics:
                self.welfarePlot = plt.axes(
                    [left, bottom, width, height],
                    sharex=self.strategiesPlot,
                    sharey=self.strategiesPlot,
                )
                self.welfarePlot.set_title("Score")
                self.welfareImage = plt.imshow(
                    games_and_strategies.rank_reduce_score(
                        implementation.currentWelfare
                    ),
                    vmin=0.0,
                    vmax=1.0,
                    cmap=self.welfareColorMap,
                )
                interticks = games_and_strategies.rank_reduce_score(
                    np.array(
                        [
                            0.0,
                            games_and_strategies.pairwiseDefectScore
                            / games_and_strategies.replicatorUpdateMaxScore,
                            games_and_strategies.pairwiseCooperateScore
                            / games_and_strategies.replicatorUpdateMaxScore,
                            1.0,
                        ]
                    )
                )
                self.welfareColorbar = plt.colorbar(
                    self.welfareImage, ticks=interticks, orientation="horizontal"
                )
                self.welfareColorbar.ax.set_xticklabels(
                    ["min", "allD", "allC", "max"], rotation=45
                )
                left += width + hsep

            if morals.safedirep in occurringMorals:
                self.safedirepPlot = plt.axes(
                    [left, bottom, width, height],
                    sharex=self.strategiesPlot,
                    sharey=self.strategiesPlot,
                )
                self.safedirepPlot.set_title("Safedirep Map")
                self.safedirepImage = plt.imshow(
                    safedirep.visualMatrix[morals.safedirep],
                    vmin=0,
                    vmax=3,
                    interpolation="nearest",
                    cmap=self.safedirepColorMap,
                    extent=(-0.5, N - 0.5, N - 0.5, -0.5),
                )
                safedirepColorBar = plt.colorbar(
                    self.safedirepImage, ticks=[0, 1, 2, 3], orientation="horizontal"
                )
                safedirepColorBar.ax.set_xticklabels(
                    ["global bad", "global good", "coop", "defect"], rotation=45
                )
                left += width + hsep

        elif display_config.showInFirstRow == display_config.perStrategyDetailedStats:
            for strategy in occurringStrategiesNames:
                self.strategyRepHistPlot[strategy] = plt.axes(
                    [left, bottom, width, height]
                )
                left += width + hsep

    def _initialize_second_row(self):
        self.strategiesDistPlot = None
        self.statsPlot = None

        if display_config.showStatsInSecondRow:
            left = border
            bottom = 1.0 - border - 2 * self.height - vsep
            width = (1.0 - 2 * border - hsep) / 2
            height = self.height

            # strategy distribution pie chart
            self.strategiesDistPlot = plt.axes([left, bottom, width, height])
            self.strategiesDistPlot.set_title("Strategies Distribution")
            left += width + hsep

            self.statsPlot = plt.axes([left, bottom, width, height], clip_on=True)
            self.barDrawWidth = (
                0.5 - 0.08 / 2 if config.welfareStatistics else 1.0
            ) / (numberOfOccurringStrategies)

    def initializeUI(self):
        # we need labels for the strategies
        self.strategiesLabels = [
            games_and_strategies.strategyName[s] for s in sorted(occurringStrategies)
        ]

        # we also need a list of the strategies names, where not-occurring are an empty string
        self.strategyLabelsWithBlanks = []
        for strategy in sorted(strategyName.keys()):
            if strategy in occurringStrategiesNames:
                self.strategyLabelsWithBlanks += [occurringStrategiesNames[strategy]]
            else:
                self.strategyLabelsWithBlanks += [""]

        self.occurringStrategiesColors = [
            display_config.strategyColor[strategy]
            for strategy in sorted(occurringStrategies)
        ]
        self.strategyColorMapDiscrete = colors.ListedColormap(
            [
                display_config.strategyColor[strategy]
                for strategy in sorted(display_config.strategyColor.keys())
            ]
        )
        self.strategyColorMapDiscrete.set_over("0.0")  # mark values out of range
        self.strategyColorMapDiscrete.set_under("0.0")

        self.diffColorMap = colors.ListedColormap(["0.0", "c", "m", "1.0"])
        self.diffColorMap.set_over("r")  # mark values out of range
        self.diffColorMap.set_under("r")

        self.lastActionColorMap = colors.ListedColormap(["g", "r"])
        self.lastActionColorMap.set_over("1.0")
        self.lastActionColorMap.set_under("0.0")

        self.safedirepColorMap = colors.ListedColormap(["0.0", "1.0", "g", "r"])
        self.safedirepColorMap.set_over("b")
        self.safedirepColorMap.set_under("b")

        # TODO replace. Currently we have [0,1] with discrete values at a*1 + b*(1+U) + c*(1-U)
        self.welfareColorMap = (
            self._compute_welfare_colormap()
        )  # plt.cm.RdYlGn   #'RdYlGn'

        self._compute_layout()
        self._initialize_first_row()
        self._initialize_second_row()

        if not display_config.completelyDisableGUI:
            plt.draw()

    def _compute_welfare_colormap(self):
        baseColormap = plt.cm.PiYG  # RdYlGn
        values = np.arange(0, 1.001, 1 / 80.0)

        def mySigmoid(x, k=5, mid=0.66):
            #    1 / (1 + Exp[-2 k (x - 1 / 2)])
            return 1 / (1 + math.exp(-2 * k * (x - mid)))

        mapped = np.array([mySigmoid(x) for x in values])
        colors = [(baseColormap(x)) for x in mapped]
        return mpl.colors.ListedColormap(colors)

    def _store_current_picture(self, iteration):
        wholeFigFilename = (
            config.foldername
            + os.sep
            + (("all-%0" + numberOfDigitsInM + "d.png") % iteration)
        )
        plt.savefig(wholeFigFilename, dpi=display_config.outputDPI, bbox_inches="tight")

    # This method is called either by the main thread (no GUI), or by the UI thread (no image thread),
    # or by the image plotter thread
    def _store_current_matrices(self, pltdata):
        iteration = pltdata.iteration

        # Store the matrices as images
        strategiesFilename = (
            config.foldername
            + os.sep
            + (("strategies-%0" + numberOfDigitsInM + "d.png") % iteration)
        )

        # get the minimal and maximal value of strategy
        minStrategyValue = min(strategyName.keys())
        maxStrategyValue = max(strategyName.keys())
        plt.imsave(
            fname=strategiesFilename,
            arr=pltdata.strategies,
            format="png",
            cmap=self.strategyColorMapDiscrete,
            vmin=minStrategyValue,
            vmax=maxStrategyValue,
        )

        for moral in occurringInterestingMorals:
            reputationFilename = (
                config.foldername
                + os.sep
                + (
                    (
                        morals.moralNames[moral]
                        + "-reputation-%0"
                        + numberOfDigitsInM
                        + "d.png"
                    )
                    % iteration
                )
            )
            plt.imsave(
                fname=reputationFilename,
                arr=pltdata.reputation[moral],
                format="png",
                cmap="hot",
                vmin=0,
                vmax=1,
            )

            if moral in pltdata.safedirepVisualMatrix:
                safedirepFname = (
                    config.foldername
                    + os.sep
                    + (
                        (
                            morals.moralNames[moral]
                            + "-direct-%0"
                            + numberOfDigitsInM
                            + "d.png"
                        )
                        % iteration
                    )
                )
                plt.imsave(
                    fname=safedirepFname,
                    arr=pltdata.safedirepVisualMatrix[moral],
                    vmin=0,
                    vmax=3,
                    format="png",
                    cmap=self.safedirepColorMap,
                )

        if config.storeMoralDiff:
            self._store_current_moral_diff_matrix(
                pltdata, config.diffMorals[0], config.diffMorals[1]
            )

        if display_config.showLastActionMatrix:
            self._store_last_action_matrix(pltdata)

        if config.welfareStatistics:
            self._store_welfare_matrix(pltdata)

    def _store_last_action_matrix(self, pltdata):
        filename = (
            config.foldername
            + os.sep
            + (("lastAction-%0" + numberOfDigitsInM + "d.png") % pltdata.iteration)
        )
        plt.imsave(
            fname=filename,
            arr=pltdata.lastAction,
            vmin=0,
            vmax=1,
            format="png",
            cmap=self.lastActionColorMap,
        )

    def _store_welfare_matrix(self, pltdata):
        filename = (
            config.foldername
            + os.sep
            + (("welfare-%0" + numberOfDigitsInM + "d.png") % pltdata.iteration)
        )
        plt.imsave(
            fname=filename,
            arr=pltdata.welfare,
            format="png",
            cmap=self.welfareColorMap,
            vmin=0,
            vmax=1.0,
        )

    def _store_current_moral_diff_matrix(self, pltdata, moral1, moral2):
        diffFilename = (
            config.foldername
            + os.sep
            + (
                (
                    "diff-"
                    + morals.moralNames[moral1]
                    + "-"
                    + morals.moralNames[moral2]
                    + "-reputation-%0"
                    + numberOfDigitsInM
                    + "d.png"
                )
                % pltdata.iteration
            )
        )

        # We implicitly assume binary reputation here!
        plt.imsave(
            fname=diffFilename,
            arr=pltdata.reputation_diff_matrix(moral1, moral2),
            format="png",
            cmap=self.diffColorMap,
            vmin=0,
            vmax=10,
        )

    def _performStores(self, pltdata):
        # Store images
        if display_config.storeMatrices:
            if not self.haveImageThread:
                self._store_current_matrices(pltdata)

        # The whole picture refers to the current frame - we cannot store that in another thread!
        if display_config.storeWholePictures:
            self._store_current_picture(pltdata.iteration)

    def _updateUI(self, pltdata, haveWindow):
        if display_config.showInFirstRow in [
            display_config.matrices,
            display_config.matricesWithRepDiff,
        ]:
            self.strategiesImage.set_array(pltdata.strategies)

            if display_config.showInFirstRow == display_config.matrices:
                self.reputationImage.set_array(
                    pltdata.reputation[display_config.guiMoral]
                )
            elif display_config.showInFirstRow == display_config.matricesWithRepDiff:
                self.reputationImage.set_array(
                    pltdata.reputation_diff_matrix(
                        config.diffMorals[0], config.diffMorals[1]
                    )
                )

            if config.welfareStatistics:
                self.welfareImage.set_array(pltdata.welfare)

            if morals.safedirep in occurringMorals:
                self.safedirepImage.set_array(
                    pltdata.safedirepVisualMatrix[morals.safedirep]
                )

        if display_config.showStatsInSecondRow:
            if next(iter(occurringStrategies)) in pltdata.statistics:
                self.strategiesDistPlot.cla()
                self.strategiesDistPlot.set_title("Strategies Distribution")
                self.strategiesDistPlot.pie(
                    pltdata.strategy_counts(),
                    labels=self.strategiesLabels,
                    autopct=lambda x: int(round(x * N * N)) / 100,
                    colors=self.occurringStrategiesColors,
                )

                self.statsPlot.cla()
                self.statsPlot.set_title(
                    "Normalized Reputation and Score by Strategy"
                    if config.welfareStatistics
                    else "Normalized Reputation by Strategy"
                )
                barStartIndex = 0.0
                self.statsPlot.set_ylim(-0.01, 1.01)
                self.statsPlot.set_xlim(-0.01, 1.01)

                for strategy in occurringStrategiesNames:
                    s = pltdata.statistics[strategy]
                    r = s[reputationStats][display_config.guiMoral]
                    repAvg = r[perMoralMean]
                    repStdAbove = r[perMoralStdevAbove]
                    repStdBelow = r[perMoralStdevBelow]
                    self.statsPlot.bar(
                        align="edge",
                        x=barStartIndex,
                        bottom=0.5,
                        height=(repAvg - 0.5),
                        width=self.barDrawWidth,
                        yerr=np.array([[repStdAbove], [repStdBelow]]),
                        color=display_config.strategyColor[strategy],
                    )

                    barStartIndex = barStartIndex + self.barDrawWidth

                if config.welfareStatistics:
                    barStartIndex += 0.08
                    for strategy in occurringStrategiesNames.keys():
                        s = pltdata.statistics[strategy]
                        wf = s[welfareStats]
                        self.statsPlot.bar(
                            align="edge",
                            x=barStartIndex,
                            height=wf,
                            bottom=0.0,
                            width=self.barDrawWidth,
                            color=display_config.strategyColor[strategy],
                        )

                        barStartIndex = barStartIndex + self.barDrawWidth

        if display_config.showInFirstRow == display_config.perStrategyDetailedStats:
            for strategy in occurringStrategiesNames.keys():
                repPlot = self.strategyRepHistPlot[strategy]
                repPlot.cla()
                repPlot.set_title("Reputation")
                selectedRep = (pltdata.reputation[display_config.guiMoral] + 10) * (
                    strategies == strategy
                ) - 10
                repPlot.hist(
                    x=selectedRep.flatten(),
                    bins=15,
                    range=(-1.01, 1.01),
                    color=display_config.strategyColor[strategy],
                )

        if haveWindow:
            try:
                self.plot.canvas.set_window_title(pltdata.title())
            except:
                pass

        self._performStores(pltdata)

    def updateUI(self):
        if self.done:
            return

        try:
            updated = False
            try:
                while True:
                    pltdata = self.queue.get_nowait()

                    if pltdata == "Q":
                        self.done = True
                        break

                    updated = True
                    self._updateUI(pltdata, not display_config.completelyDisableGUI)
            except Empty:
                pass

            if not display_config.completelyDisableGUI and updated:
                plt.draw()

        except Exception:
            print("Error in UI update: " + traceback.format_exc())

    def refreshUI(self, iteration):
        pltdata = PlotData(iteration)

        if display_config.completelyDisableGUI:
            pltdata.statistics = statistics
            pltdata.strategies = strategies
            pltdata.reputation = reputation

            if config.welfareStatistics:
                pltdata.welfare = games_and_strategies.rank_reduce_score(
                    implementation.currentWelfare
                )

            if display_config.showLastActionMatrix:
                pltdata.lastAction = implementation.lastAction

            pltdata.safedirepVisualMatrix = safedirep.visualMatrix

        else:
            pltdata.statistics = deepcopy(current)
            pltdata.strategies = deepcopy(strategies)
            pltdata.reputation = deepcopy(reputation)

            if display_config.showLastActionMatrix:
                pltdata.lastAction = deepcopy(implementation.lastAction)

            if config.welfareStatistics:
                pltdata.welfare = games_and_strategies.rank_reduce_score(
                    implementation.currentWelfare
                )

            pltdata.safedirepVisualMatrix = deepcopy(safedirep.visualMatrix)

        self.queue.put(pltdata)

        if self.haveImageThread:
            self.imagequeue.put(pltdata)
        elif display_config.completelyDisableGUI:
            self.updateUI()

    def signalDone(self):
        self.queue.put("Q")

        if self.haveImageThread:
            self.imagequeue.put("Q")

    def _runUntilDone(self):
        while True:
            pltdata = self.queue.get()

            if pltdata == "Q":
                self.done = True
                return "Q"

            try:
                self._updateUI(pltdata, False)
            except Exception:
                print("Error in UI update: " + traceback.format_exc())

    def _plotImagesMain(self):
        while True:
            pltdata = self.imagequeue.get()

            if pltdata == "Q":
                return

            try:
                self._store_current_matrices(pltdata)
            except Exception:
                print("Error while storing images: " + traceback.format_exc())

    def main(self, simulationMethod):
        if display_config.completelyDisableGUI:
            simulationMethod(self)
            self.done = True
        else:
            self.thread = threading.Thread(
                target=lambda: simulationMethod(self), name="simulationThread"
            )
            self.thread.start()

            if self.haveImageThread:
                self.imagethread.start()

            self.timer = self.plot.canvas.new_timer(interval=plotUpdateInterval)
            self.timer.add_callback(_after, (self))
            self.timer.start()

            plt.show()

            if not self.done:
                self._runUntilDone()
            self.thread.join()

            if self.haveImageThread:
                self.imagethread.join()
