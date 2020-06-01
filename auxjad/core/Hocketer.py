import copy
import random
import abjad
from ..utilities.rests_to_multimeasure_rest import rests_to_multimeasure_rest


class Hocketer():
    r"""Hocketer is a hocket generator. It takes an input ``abjad.Container``
    and randomly distribute its logical ties among different staves, filling
    the empty durations with rests.

    ..  container:: example

        Calling the object will output a tuple of staves generated by the
        hocket process.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> hocketer = auxjad.Hocketer(container)
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                r2
                e'4
                r4
            }
            \new Staff
            {
                c'4
                d'4
                r4
                f'4
            }
        >>

        .. figure:: ../_images/image-Hocketer-1.png

        To get the result of the last operation, use the property
        ``current_window``.

        >>> music = hocketer.current_window
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                r2
                e'4
                r4
            }
            \new Staff
            {
                c'4
                d'4
                r4
                f'4
            }
        >>

        .. figure:: ../_images/image-Hocketer-2.png

    ..  container:: example

        This class has many keyword arguments, all of which can be altered
        after instantiation using properties with the same names as shown
        below.

        >>> container = abjad.Container(r"\time 3/4 c'4 d'4 e'4 | f'4 g'4 a'4")
        >>> hocketer = auxjad.Hocketer(container,
        ...                            n_voices=3,
        ...                            weights=[1, 2, 5],
        ...                            k=2,
        ...                            disable_rewrite_meter=True,
        ...                            use_multimeasure_rests=False,
        ...                            )
        >>> hocketer.n_voices
        3
        >>> hocketer.weights
        [1, 2, 5]
        >>> hocketer.k
        2
        >>> hocketer.disable_rewrite_meter
        True
        >>> not hocketer.use_multimeasure_rests
        False
        >>> hocketer.n_voices = 5
        >>> hocketer.weights = [1, 1, 1, 2, 7]
        >>> hocketer.k = 3
        >>> hocketer.disable_rewrite_meter = False
        >>> hocketer.use_multimeasure_rests = True
        >>> hocketer.n_voices
        5
        >>> hocketer.weights
        [1, 1, 1, 2, 7]
        >>> hocketer.k
        3
        >>> not hocketer.disable_rewrite_meter
        False
        >>> hocketer.use_multimeasure_rests
        True

    ..  container:: example

        Use the optional argument ``n_voices`` to set the number of different
        staves in the output (default is 2).

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c''8")
        >>> hocketer = auxjad.Hocketer(container, n_voices=3)
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                c'8
                r8
                e'8
                r8
                g'8
                r4.
            }
            \new Staff
            {
                r8
                d'8
                r4.
                a'8
                r4
            }
            \new Staff
            {
                r4.
                f'8
                r4
                b'8
                c''8
            }
        >>

        .. figure:: ../_images/image-Hocketer-3.png

    ..  container:: example

        Applying the ``len()`` function to the hocketer will return the current
        number of voices to be output by the hocketer.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4 ~ | f'2 g'2")
        >>> hocketer = auxjad.Hocketer(container, n_voices=7)
        >>> len(hocketer)
        6

    ..  container:: example

        Set ``weights`` to a list of numbers (either floats or integers) to
        give different weights to each voice. By default, all voices have equal
        weight. The list in ``weights`` must have the same length as the number
        of voices. In the example below, ``weights`` is set to a list of length
        2 (matching the default two voices). The second voice has a higher
        weight to it, and receives more notes from the hocket process as
        expected.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c''8")
        >>> hocketer = auxjad.Hocketer(container,
        ...                            weights=[2.1, 5.7],
        ...                            )
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                r8
                d'8
                r4
                g'8
                r4.
            }
            \new Staff
            {
                c'8
                r8
                e'8
                f'8
                r8
                a'8
                b'8
                c''8
            }
        >>

        .. figure:: ../_images/image-Hocketer-5.png

        Use the method ``reset_weights()`` to reset the weights back to their
        default values.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c''8")
        >>> hocketer = auxjad.Hocketer(container,
        ...                            weights=[2.1, 5.7],
        ...                            )
        >>> hocketer.weights
        [2.1, 5.7]
        >>> hocketer.reset_weights()
        >>> hocketer.weights
        [1.0, 1.0]

    ..  container:: example

        Set ``k`` to an integer representing how many times each logical tie
        is fed into the hocket process. By default, ``k`` is set to ``1``, so
        each logical tie is assigned to a single voice. Changing this to a
        higher value will increase the chance of a logical tie appearing for
        up to ``k`` different voices.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> hocketer = auxjad.Hocketer(container, n_voices=4, k=2)
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.show(score)
        \new Score
        <<
            \new Staff
            {
                c'4
                d'4
                e'4
                r4
            }
            \new Staff
            {
                r2
                e'4
                f'4
            }
            \new Staff
            {
                r2.
                f'4
            }
            \new Staff
            {
                r4
                d'4
                r2
            }
        >>

        .. figure:: ../_images/image-Hocketer-5.png

    ..  container:: example

        By default, this class rewrites uses abjad's ``rewrite_meter()``
        mutation, which is necessary for cleaning up the rests.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c''8")
        >>> hocketer = auxjad.Hocketer(container)
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                c'8
                d'8
                r4.
                a'8
                r4
            }
            \new Staff
            {
                r4
                e'8
                f'8
                g'8
                r8
                b'8
                c''8
            }
        >>

        .. figure:: ../_images/image-Hocketer-6.png

        Set ``disable_rewrite_meter`` to ``True`` in order to disable this
        behaviour.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c''8")
        >>> hocketer = auxjad.Hocketer(container,
        ...                            disable_rewrite_meter=True,
        ...                            )
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                c'8
                d'8
                r8
                r8
                r8
                a'8
                r8
                r8
            }
            \new Staff
            {
                r8
                r8
                e'8
                f'8
                g'8
                r8
                b'8
                c''8
            }
        >>

        .. figure:: ../_images/image-Hocketer-7.png

    ..  container:: example

        By default, this class rewrites all bars that are filled with rests,
        replacing the rests by a multi-measure rest.

        >>> container = abjad.Container(r"\time 3/4 c'4 d'4 e'4 f'4 g'4 a'4")
        >>> hocketer = auxjad.Hocketer(container)
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                \time 3/4
                R1 * 3/4
                r4
                g'4
                a'4
            }
            \new Staff
            {
                \time 3/4
                c'4
                d'4
                e'4
                f'4
                r2
            }
        >>

        .. figure:: ../_images/image-Hocketer-8.png

        Set ``use_multimeasure_rests`` to ``False`` to disable this behaviour.

        >>> container = abjad.Container(r"\time 3/4 c'4 d'4 e'4 f'4 g'4 a'4")
        >>> hocketer = auxjad.Hocketer(container,
        ...                            use_multimeasure_rests=False,
        ...                            )
        >>> music = hocketer()
        >>> score = abjad.Score(music)
        >>> abjad.f(score)
        \new Score
        <<
            \new Staff
            {
                \time 3/4
                r2.
                r4
                g'4
                a'4
            }
            \new Staff
            {
                \time 3/4
                c'4
                d'4
                e'4
                f'4
                r2
            }
        >>

        .. figure:: ../_images/image-Hocketer-9.png

    ..  container:: example

        Use the property ``contents`` to get the input container upon which the
        hocketer operates. Notice that ``contents`` remains invariant after
        any shuffling or rotation operations (use ``current_window`` for the
        transformed selection of music). ``contents`` can be used to change the
        ``abjad.Container`` to be shuffled.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> hocketer = auxjad.Hocketer(container)
        >>> abjad.f(hocketer.contents)
        {
            c'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-Hocketer-10.png

        >>> hocketer()
        >>> abjad.f(hocketer.contents)
        {
            c'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-Hocketer-11.png

        >>> hocketer.contents = abjad.Container(r"cs2 ds2")
        >>> abjad.f(hocketer.contents)
        {
            cs2
            ds2
        }

        .. figure:: ../_images/image-Hocketer-12.png
    """

    ### CLASS VARIABLES ###

    __slots__ = ('_contents',
                 '_n_voices',
                 '_weights',
                 '_k',
                 '_disable_rewrite_meter',
                 '_use_multimeasure_rests',
                 '_voices',
                 '_time_signatures',
                 )

    ### INITIALISER ###

    def __init__(self,
                 contents: abjad.Container,
                 *,
                 n_voices: int = 2,
                 weights: list = None,
                 k: int = 1,
                 disable_rewrite_meter: bool = False,
                 use_multimeasure_rests: bool = True,
                 ):
        r'Initialises self.'
        self.contents = contents
        self.n_voices = n_voices
        if weights:
            self.weights = weights
        else:
            self.reset_weights()
        self.k = k
        self.disable_rewrite_meter = disable_rewrite_meter
        self.use_multimeasure_rests = use_multimeasure_rests

    ### SPECIAL METHODS ###

    def __repr__(self) -> str:
        r'Returns interpret representation of ``contents``.'
        return format(self._contents)

    def __len__(self) -> int:
        r'Returns the number of voices of the hocketer.'
        return self._n_voices

    def __call__(self) -> abjad.Selection:
        r'Calls the shuffling process, returning an ``abjad.Container``'
        self._hocket_process()
        return (abjad.Staff([copy.deepcopy(voice)]) for voice in self._voices)

    def __getitem__(self, key: int):
        r"""Returns one or more voices of the output of the hocketer through
        indexing or slicing.
        """
        return copy.deepcopy(self._voices[key])

    ### PUBLIC METHODS ###

    def reset_weights(self):
        r'Resets the weight vector of all voices to an uniform distribution.'
        self.weights = [1.0 for _ in range(self.__len__())]

    ### PRIVATE METHODS ###

    def _hocket_process(self):
        r"""Runs the hocket process, returning a tuple of
        ``abjad.Container()``. It distributes the logical ties from the
        ``contents`` into different voices. Voices can have different weights,
        and the process of distributing a same logical tie can be run more than
        once (defined by the attribute ``k``).
        """
        dummy_voices = [abjad.Container() for _ in range(self.n_voices)]

        for logical_tie in abjad.select(self.contents).logical_ties():
            selected_voices = random.choices([n for n in range(self.n_voices)],
                                             weights=self.weights,
                                             k=self.k,
                                             )
            for voice in dummy_voices:
                if dummy_voices.index(voice) in selected_voices:
                    voice.append(copy.deepcopy(logical_tie))
                else:
                    for leaf in logical_tie:
                        rest = abjad.Rest(leaf.written_duration)
                        for indicator in abjad.inspect(leaf).indicators():
                            if isinstance(indicator, abjad.TimeSignature):
                                abjad.attach(indicator, rest)
                        voice.append(rest)

        if not self._disable_rewrite_meter:
            for dummy_voice in dummy_voices:
                start = 0
                duration = abjad.Duration(0)
                index = 0
                dummy_voice_leaves = abjad.select(dummy_voice).leaves()
                for leaf_n in range(len(dummy_voice_leaves)):
                    duration = abjad.inspect(
                        dummy_voice_leaves[start : leaf_n+1]).duration()
                    if duration == self._time_signatures[index].duration:
                        abjad.mutate(
                            dummy_voice_leaves[start : leaf_n+1]
                        ).rewrite_meter(self._time_signatures[index])
                        if index + 1 < len(self._time_signatures):
                            index += 1
                            start = leaf_n + 1
                        else:
                            break

        if self._use_multimeasure_rests:
            for dummy_voice in dummy_voices:
                rests_to_multimeasure_rest(dummy_voice)

        # output
        self._voices = []
        for dummy_voice in dummy_voices:
            self._voices.append(dummy_voice[:])
            dummy_voice[:] = []

    def _find_time_signatures(self):
        r"""Creates a list of all time signatures for all measures of
        ``contents``.
        """
        self._time_signatures = []
        leaves = abjad.select(self._contents).leaves()
        duration = abjad.Duration(0)
        time_signature = abjad.inspect(
            leaves[0]).effective(abjad.TimeSignature)
        if not time_signature:
            time_signature = abjad.TimeSignature((4, 4))
        for leaf in leaves:
            if duration % time_signature.duration == 0:
                time_signature = abjad.inspect(
                    leaf).effective(abjad.TimeSignature)
                if time_signature:
                    duration = abjad.Duration(0)
                elif leaf is leaves[0]:
                    time_signature = abjad.TimeSignature((4, 4))
                else:
                    time_signature = self._time_signatures[-1]
                self._time_signatures.append(time_signature)
            duration += abjad.inspect(leaf).duration()

    ### PUBLIC PROPERTIES ###

    @property
    def contents(self) -> abjad.Container:
        r'The ``abjad.Container`` to be hocketed.'
        return self._contents

    @contents.setter
    def contents(self,
                 contents: abjad.Container
                 ):
        if not isinstance(contents, abjad.Container):
            raise TypeError("'contents' must be 'abjad.Container' or child "
                            "class")
        self._contents = copy.deepcopy(contents)
        self._find_time_signatures()

    @property
    def n_voices(self) -> int:
        r'Number of individual voices in the output.'
        return self._n_voices

    @n_voices.setter
    def n_voices(self,
                 n_voices: int,
                 ):
        if not isinstance(n_voices, int):
            raise TypeError("'n_voices' must be 'int'")
        if n_voices < 1:
            raise ValueError("'n_voices' must be greater than zero")
        self._n_voices = n_voices

    @property
    def weights(self) -> list:
        r'The ``list`` with weights for each voice.'
        return self._weights

    @weights.setter
    def weights(self,
                weights: list,
                ):
        if not isinstance(weights, list):
            raise TypeError("'weights' must be 'list'")
        if not self.__len__() == len(weights):
            raise ValueError("'weights' must have the same length as "
                             "'n_voices'")
        if not all(isinstance(weight, (int, float))
                   for weight in weights):
            raise TypeError("'weights' elements must be 'int' or 'float'")
        self._weights = weights[:]

    @property
    def k(self) -> int:
        r'Number of random choice operations applied to a logical tie.'
        return self._k

    @k.setter
    def k(self,
          k: int,
          ):
        if not isinstance(k, int):
            raise TypeError("'k' must be 'int'")
        if k < 1:
            raise ValueError("'k' must be greater than zero")
        self._k = k

    @property
    def disable_rewrite_meter(self) -> bool:
        r"""When ``True``, the durations of the notes in the output will not be
        rewritten by the ``rewrite_meter`` mutation. Rests will have the same
        duration as the logical ties they replaced.
        """
        return self._disable_rewrite_meter

    @disable_rewrite_meter.setter
    def disable_rewrite_meter(self,
                              disable_rewrite_meter: bool,
                              ):
        if not isinstance(disable_rewrite_meter, bool):
            raise TypeError("'disable_rewrite_meter' must be 'bool'")
        self._disable_rewrite_meter = disable_rewrite_meter

    @property
    def use_multimeasure_rests(self) -> bool:
        r"""When ``True``, the rests in any bars filled only with rests will be
        replaced by a multi-measure rest.
        """
        return self._use_multimeasure_rests

    @use_multimeasure_rests.setter
    def use_multimeasure_rests(self,
                              use_multimeasure_rests: bool,
                              ):
        if not isinstance(use_multimeasure_rests, bool):
            raise TypeError("'use_multimeasure_rests' must be 'bool'")
        self._use_multimeasure_rests = use_multimeasure_rests

    @property
    def current_window(self) -> abjad.Selection:
        r'Read-only property, returns the result of the last operation.'
        return (abjad.Staff([copy.deepcopy(voice)]) for voice in self._voices)
