import random
from typing import Optional, Union

import abjad

from ..utilities.remove_repeated_dynamics import remove_repeated_dynamics
from ..utilities.remove_repeated_time_signatures import (
    remove_repeated_time_signatures,
)
from .TenneySelector import TenneySelector


class PitchRandomiser:
    r"""``PitchRandomiser`` takes an input ``abjad.Container`` (or child class)
    and a series of pitches and randomises the container's pitches using that
    list. The pitches can be of type ``list``, ``tuple``, ``str``, or
    ``abjad.PitchSegment``.

    Example:
        Calling the object will output a selection of the input container with
        randomised pitches. Pitches are randomly selected from ``pitches``.

        >>> container = abjad.Container(r"\time 4/4 c'4 d'4 e'4 f'4")
        >>> pitches = r"fs' gs' a' b' cs''"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            a'4
            b'4
            cs''4
            fs'4
        }

        .. figure:: ../_images/image-PitchRandomiser-1.png

        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            b'4
            b'4
            b'4
            fs'4
        }

        .. figure:: ../_images/image-PitchRandomiser-2.png

        To get the result of the last operation, use the property
        ``current_window``.

        >>> notes = randomiser.current_window
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            b'4
            b'4
            b'4
            fs'4
        }

        .. figure:: ../_images/image-PitchRandomiser-3.png

    ..  warning::

        Unlike the other classes in Auxjad, the very first call of
        ``PitchRandomiser`` will already process the initial container. To
        disable this behaviour and output the initial container once before
        randomising its pitches, initialise the class with the keyword argument
        ``processs_on_first_call`` set to ``False``.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     processs_on_first_call=False,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-PitchRandomiser-4.png

        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            b'4
            fs'4
            gs'4
            fs'4
        }

        .. figure:: ../_images/image-PitchRandomiser-5.png

    Example:
        Applying the ``len()`` function to the randomiser will return the
        number of pitches in ``pitches``.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> len(randomiser)
        4

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> pitches = [6, 7, 8, 9, 10, 11, 12]
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> len(randomiser)
        7

    Example:
        This class has many keyword arguments, all of which can be altered
        after instantiation using properties with the same names as shown
        below. ``weights`` takes a list of ``int``'s or ``float``'s
        representing the weight of each pitch from ``pitches`` (their lengthes
        must also match). ``omit_time_signatures`` will remove all time
        signatures from the output (both are ``False`` by default).
        ``processs_on_first_call`` to ``True`` and the random pitch process
        will be applied on the very first call. Setting ``use_tenney_selector``
        to ``True`` will make the randomiser use ``auxjad.TenneySelector`` for
        the random selection instead of ``random.choices()`` (default is
        ``False``).

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> randomiser = auxjad.PitchRandomiser(
        ...     container,
        ...     pitches=r"a b cs' ds' e'",
        ...     weights=[1.0, 2.0, 1.0, 1.5, 1.3],
        ...     omit_time_signatures=True,
        ...     processs_on_first_call=True,
        ...     use_tenney_selector=True,
        ... )
        >>> randomiser.pitches
        <a b cs' ds' e'>
        >>> randomiser.weights
        [1.0, 2.0, 1.0, 1.5, 1.3]
        >>> randomiser.omit_time_signatures
        True
        >>> randomiser.processs_on_first_call
        True
        >>> randomiser.use_tenney_selector
        True

        Use the properties below to change these values after initialisation.

        >>> randomiser.pitches = abjad.PitchSegment(r"c' d' e' f'")
        >>> randomiser.weights = [1, 2, 5, 8]
        >>> randomiser.omit_time_signatures = False
        >>> randomiser.processs_on_first_call = False
        >>> randomiser.use_tenney_selector = False
        >>> assert randomiser.pitches
        <c' d' e' f'>
        >>> assert randomiser.weights
        [1, 2, 5, 8]
        >>> randomiser.omit_time_signatures
        False
        >>> randomiser.processs_on_first_call
        False
        >>> randomiser.use_tenney_selector
        False

    Example:
        Only pitched logical ties are randomised, rests are left untouched.

        >>> container = abjad.Container(r"c'8. d'4 r8 r8. e'16 f'8.")
        >>> pitches = [6, 7, 8, 9, 10, 11]
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            bf'8.
            af'4
            r8
            r8.
            bf'16
            a'8.
        }

        .. figure:: ../_images/image-PitchRandomiser-6.png

    Example:
        Each note of a chord is randomised too.

        >>> container = abjad.Container(
        ...     r"<c' e' g'>8. d'4 r8 r8. e'16 <f' a'>8.")
        >>> pitches = [6, 7, 8, 9, 10, 11]
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            <fs' g' bf'>8.
            b'4
            r8
            r8.
            bf'16
            <fs' bf'>8.
        }

        .. figure:: ../_images/image-PitchRandomiser-7.png

        The number of note heads in a chord stay the same unless there are
        fewer pitches available in ``pitches``.

        >>> container = abjad.Container(
        ...     r"<c' e' g' a'>2 <cs' ds' e' f' g' a' b'>2")
        >>> pitches = [6, 7, 8]
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            <fs' g' af'>2
            <fs' g' af'>2
        }

        .. figure:: ../_images/image-PitchRandomiser-8.png

    Example:
        Setting ``use_tenney_selector`` to ``True`` will make the randomiser
        use ``auxjad.TenneySelector`` for the random selection instead of
        ``random.choices()`` (default is ``False``). ``TenneySelector`` will
        raise the chance of a pitch being selected the longer it hasn't been
        selected, and will forbid immediate repetitions of pitches. See its
        documentation for more information.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c'8")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     use_tenney_selector=True,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            fs'8
            a'8
            fs'8
            gs'8
            a'8
            b'8
            gs'8
            fs'8
        }

        .. figure:: ../_images/image-PitchRandomiser-9.png

    Example:
        Individual pitches can have different weights, defined by the
        ``weights`` property. It takes a ``list`` of ``float``'s or ``int``'s.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c'8")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     weights=[5.0, 2.0, 1.5, 1.0],
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            b'8
            fs'8
            gs'8
            gs'8
            gs'8
            fs'8
            fs'8
            a'8
        }

        .. figure:: ../_images/image-PitchRandomiser-10.png

    Example:
        Non-uniform ``weights`` can also be used when ``use_tenney_selector``
        is set to ``True``.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c'8")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     weights=[5.0, 2.0, 1.5, 1.0],
        ...                                     use_tenney_selector=True,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            fs'8
            gs'8
            a'8
            fs'8
            gs'8
            a'8
            gs'8
            b'8
        }

        .. figure:: ../_images/image-PitchRandomiser-11.png

    Example:
        Setting the weights to ``None`` will reset it back to a uniform
        distribution.

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c'8")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     weights=[100.0, 1.0, 1.0, 1.0],
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            fs'8
            fs'8
            fs'8
            fs'8
            fs'8
            fs'8
            fs'8
            fs'8
        }

        .. figure:: ../_images/image-PitchRandomiser-12.png

        >>> randomiser.weights = None
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            fs'8
            fs'8
            b'8
            gs'8
            gs'8
            a'8
            fs'8
            b'8
        }

        .. figure:: ../_images/image-PitchRandomiser-13.png

    Example:
        When using a custom list of ``weights``, changing the ``pitches`` to a
        series of new values with the same length will preserve the ``weights``
        values. If on the other hand ``pitches`` changes in length, ``weights``
        is reset to ``None`` (i.e. uniform distribution).

        >>> container = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c'8")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     weights=[100.0, 1.0, 1.0, 1.0],
        ...                                     )
        >>> randomiser.pitches = r"c'' d'' e'' f''"
        >>> randomiser.pitches
        <c'' d'' e'' f''>
        >>> randomiser.weights
        [100.0, 1.0, 1.0, 1.0]
        >>> randomiser.pitches = r"c'' d'' e'' f'' g'' a'' b''"
        >>> randomiser.pitches
        <c'' d'' e'' f'' g'' a'' b''>
        >>> randomiser.weights
        None

    ..  error::

        Note that ``weights`` must always have the same length as ``pitches``.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> pitches = r"fs' gs' a' b'"
        >>> weights = [1, 1, 5, 2, 3, 4, 8]
        >>> auxjad.PitchRandomiser(container, pitches, weights=weights)
        ValueError: 'weights' must have the same length as 'pitches'

    Example:
        To output several randomised containers at once, use the method
        ``output_n()``, inputting the desired number of iterations.

        >>> container = abjad.Container(r"c'4 ~ c'16 r8. d'4 e'8. r16")
        >>> pitches = [6, 7, 8, 9, 10]
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> notes = randomiser.output_n(3)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            a'4
            ~
            a'16
            r8.
            g'4
            fs'8.
            r16
            g'4
            ~
            g'16
            r8.
            g'4
            fs'8.
            r16
            bf'4
            ~
            bf'16
            r8.
            a'4
            af'8.
            r16
        }

        .. figure:: ../_images/image-PitchRandomiser-14.png

    Example:
        This class preserves indicators.

        >>> container = abjad.Container(
        ...     r"c'4\p\< ~ c'8. d'16-.\f e'4--\pp f'8.( g'16)")
        >>> pitches = [6, 7, 8, 9, 10, 11, 12]
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            a'4
            \p
            \<
            ~
            a'8.
            c''16
            \f
            - \staccato
            af'4
            \pp
            - \tenuto
            a'8.
            (
            bf'16
            )
        }

        .. figure:: ../_images/image-PitchRandomiser-15.png

    Example:
        This class also preserves the time signature structure.

        >>> container = abjad.Container(
        ...     r"\time 3/4 c'4 d'2 \time 2/4 e'8 f'8 g'8 a'8")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            a'4
            fs'2
            \time 2/4
            gs'8
            gs'8
            a'8
            gs'8
        }

        .. figure:: ../_images/image-PitchRandomiser-16.png

    Example:
        To omit time signatures altogether, set ``omit_time_signatures`` to
        ``True`` (default is ``False``).

        >>> container = abjad.Container(
        ...     r"\time 3/4 c'4 d'2 \time 2/4 e'8 f'8 g'8 a'8")
        >>> pitches = r"fs' gs' a' b'"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     omit_time_signatures=True,
        ...                                     )
        >>> notes = randomiser()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            a'4
            fs'2
            gs'8
            gs'8
            a'8
            gs'8
        }

        .. figure:: ../_images/image-PitchRandomiser-17.png

    Example:
        The instances of ``PitchRandomiser`` can also be used as an iterator,
        which can then be used in a for loop. Note that unlike the method
        ``output_n()``, time signatures are added to each window returned by
        the randomiser. Use the function
        ``auxjad.remove_repeated_time_signatures()`` to clean the output when
        using ``PitchRandomiser`` in this way. It is also important to note
        that a ``break`` statement is needed when using ``PitchRandomiser`` as
        an iterator. The reason is that pitch randomisation is a process that
        can happen indefinitely (unlike some of the other classes in this
        library).

        >>> container = abjad.Container(r"\time 3/4 c'4 d'4 e'4")
        >>> pitches = r"fs' gs' a' b' cs''"
        >>> randomiser = auxjad.PitchRandomiser(container,
        ...                                     pitches,
        ...                                     )
        >>> staff = abjad.Staff()
        >>> for window in randomiser:
        ...     staff.append(window)
        ...     if abjad.inspect(staff).duration() == abjad.Duration((9, 4)):
        ...         break
        >>> auxjad.remove_repeated_time_signatures(staff)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            a'4
            b'4
            gs'4
            fs'4
            a'4
            b'4
            a'4
            gs'4
            cs''4
        }

        .. figure:: ../_images/image-PitchRandomiser-18.png

    .. tip::

        The functions ``auxjad.remove_repeated_dynamics()`` and
        ``auxjad.reposition_clefs()`` can be used to clean the output and
        remove repeated dynamics and unnecessary clef changes.
    """

    ### CLASS VARIABLES ###

    __slots__ = ('_contents',
                 '_pitches',
                 '_weights',
                 '_omit_time_signatures',
                 '_processs_on_first_call',
                 '_use_tenney_selector',
                 '_tenney_selector',
                 '_current_window',
                 '_is_first_window',
                 )

    ### INITIALISER ###

    def __init__(self,
                 contents: abjad.Container,
                 pitches: Union[list, tuple, str, abjad.PitchSegment],
                 *,
                 weights: Optional[list] = None,
                 omit_time_signatures: bool = False,
                 processs_on_first_call: bool = True,
                 use_tenney_selector: bool = False,
                 ):
        r'Initialises self.'
        self.contents = contents
        self._weights = []
        self.pitches = pitches
        self.weights = weights
        self.omit_time_signatures = omit_time_signatures
        self.processs_on_first_call = processs_on_first_call
        self.use_tenney_selector = use_tenney_selector
        self._is_first_window = True

    ### SPECIAL METHODS ###

    def __repr__(self) -> str:
        r'Returns interpreter representation of ``pitches``.'
        return repr(self._pitches)

    def __len__(self) -> int:
        r'Returns the number of available ``pitches``.'
        return len(self._pitches)

    def __call__(self) -> abjad.Selection:
        r'Calls the randomise process, returning an ``abjad.Selection``'
        self._randomise()
        return self.current_window

    def __next__(self) -> abjad.Selection:
        r"""Calls the randomise process for one iteration, returning an
        ``abjad.Selection``.
        """
        return self.__call__()

    def __iter__(self):
        r'Returns an iterator, allowing instances to be used as iterators.'
        return self

    ### PUBLIC METHODS ###

    def output_n(self,
                 n: int,
                 ) -> abjad.Selection:
        r"""Goes through ``n`` iterations of the pitch randomisation process
        and outputs a single ``abjad.Selection``.
        """
        if not isinstance(n, int):
            raise TypeError("argument must be 'int'")
        if n < 1:
            raise ValueError("argument must be greater than zero")
        dummy_container = abjad.Container()
        for _ in range(n):
            dummy_container.append(self.__call__())
        remove_repeated_time_signatures(dummy_container)
        remove_repeated_dynamics(dummy_container)
        output = dummy_container[:]
        dummy_container[:] = []
        return output

    ### PRIVATE METHODS ###

    def _randomise(self) -> abjad.Selection:
        r'Randomises pitches of ``contents``.'
        if self._is_first_window and not self._processs_on_first_call:
            self._is_first_window = False
        else:
            self._rewrite_pitches()

    def _rewrite_pitches(self):
        r'Rewrites the pitches of the current window.'
        dummy_container = abjad.mutate(self._contents).copy()
        logical_ties = abjad.select(dummy_container).logical_ties()
        for logical_tie in logical_ties:
            if isinstance(logical_tie[0], abjad.Note):
                pitch = self._pick_random_pitch()
                for leaf in logical_tie:
                    leaf.written_pitch = pitch
            elif isinstance(logical_tie[0], abjad.Chord):
                chord_n = len(logical_tie[0].written_pitches)
                if chord_n > self.__len__():
                    pitches = self._pitches
                else:
                    pitches = []
                    while len(pitches) < chord_n:
                        pitch = self._pick_random_pitch()
                        if pitch not in pitches:
                            pitches.append(pitch)
                for leaf in logical_tie:
                    leaf.written_pitches = pitches
        # output
        self._is_first_window = False
        self._current_window = dummy_container[:]
        dummy_container[:] = []

    def _pick_random_pitch(self) -> abjad.Pitch:
        r"""Random pitch selector, using either ``random.choices()`` or
        ``auxjad.TenneySelector``.
        """
        if not self._use_tenney_selector:
            return random.choices(self._pitches,
                                  weights=self._weights,
                                  )[0]
        else:
            return self._tenney_selector()

    @staticmethod
    def _remove_all_time_signatures(container):
        r'Removes all time signatures of an ``abjad.Container``.'
        for leaf in abjad.select(container).leaves():
            if abjad.inspect(leaf).effective(abjad.TimeSignature):
                abjad.detach(abjad.TimeSignature, leaf)

    ### PUBLIC PROPERTIES ###

    @property
    def contents(self) -> abjad.Container:
        r'The ``abjad.Container`` to be shuffled.'
        return abjad.mutate(self._contents).copy()

    @contents.setter
    def contents(self,
                 contents: abjad.Container,
                 ):
        if not isinstance(contents, abjad.Container):
            raise TypeError("'contents' must be 'abjad.Container' or child "
                            "class")
        if not abjad.select(contents).leaves().are_contiguous_logical_voice():
            raise ValueError("'contents' must be contiguous logical voice")
        if isinstance(contents, abjad.Score):
            self._contents = abjad.mutate(contents[0]).copy()
        elif isinstance(contents, abjad.Tuplet):
            self._contents = abjad.Container([abjad.mutate(contents).copy()])
        else:
            self._contents = abjad.mutate(contents).copy()
        dummy_container = abjad.mutate(contents).copy()
        self._current_window = dummy_container[:]
        dummy_container[:] = []
        self._is_first_window = True

    @property
    def pitches(self) -> abjad.PitchSegment:
        r'Pitches available for the randomiser.'
        return self._pitches

    @pitches.setter
    def pitches(self,
                pitches: Union[list, tuple, str, abjad.PitchSegment],
                ):
        if not isinstance(pitches, (list, tuple, str, abjad.PitchSegment)):
            raise TypeError("'pitches' must be 'list', 'tuple', 'str', or "
                            "'abjad.PitchSegment'")
        if isinstance(pitches, (list, tuple, str)):
            self._pitches = abjad.PitchSegment(pitches)
        else:
            self._pitches = pitches
        pitch_list = [pitch for pitch in self._pitches]
        self._tenney_selector = TenneySelector(pitch_list)
        if self._weights is not None:
            if len(pitch_list) != len(self._weights):
                self.weights = None

    @property
    def weights(self) -> list:
        r'The ``list`` with weights for each element of ``pitches``'
        return self._weights

    @weights.setter
    def weights(self,
                weights: list,
                ):
        if weights is not None:
            if not isinstance(weights, list):
                raise TypeError("'weights' must be 'list'")
            if not self.__len__() == len(weights):
                raise ValueError("'weights' must have the same length as "
                                 "'pitches'")
            if not all(isinstance(weight, (int, float))
                       for weight in weights):
                raise TypeError("'weights' elements must be 'int' or 'float'")
            self._weights = weights[:]
        else:
            self._weights = None
        self._tenney_selector.weights = self._weights

    @property
    def omit_time_signatures(self) -> bool:
        r'When ``True``, the output will contain no time signatures.'
        return self._omit_time_signatures

    @omit_time_signatures.setter
    def omit_time_signatures(self,
                             omit_time_signatures: bool,
                             ):
        if not isinstance(omit_time_signatures, bool):
            raise TypeError("'omit_time_signatures' must be 'bool'")
        self._omit_time_signatures = omit_time_signatures

    @property
    def processs_on_first_call(self) -> bool:
        r"""If ``True`` then the ``contents`` will be processed in the very
        first call.
        """
        return self._processs_on_first_call

    @processs_on_first_call.setter
    def processs_on_first_call(self,
                               processs_on_first_call: bool,
                               ):
        if not isinstance(processs_on_first_call, bool):
            raise TypeError("'processs_on_first_call' must be 'bool'")
        self._processs_on_first_call = processs_on_first_call

    @property
    def use_tenney_selector(self) -> bool:
        r"""If ``True`` then the pitches will be selected using
        ``TenneySelector``, otherwise they are chosen using a uniform random
        distribution.
        """
        return self._use_tenney_selector

    @use_tenney_selector.setter
    def use_tenney_selector(self,
                            use_tenney_selector: bool,
                            ):
        if not isinstance(use_tenney_selector, bool):
            raise TypeError("'use_tenney_selector' must be 'bool'")
        self._use_tenney_selector = use_tenney_selector

    @property
    def current_window(self) -> abjad.Selection:
        r'Read-only property, returns the result of the last operation.'
        current_window = abjad.mutate(self._current_window).copy()
        if self._omit_time_signatures:
            self._remove_all_time_signatures(current_window)
        return current_window
