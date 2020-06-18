import copy
import random
import abjad
from ..utilities.enforce_time_signature import enforce_time_signature
from ..utilities.time_signature_extractor import time_signature_extractor
from ..utilities.rests_to_multimeasure_rest import rests_to_multimeasure_rest


class Fader():
    r"""This class can be used to fade in or fade out an ``abjad.Container`` by
    gradually removing or adding its logical ties one by one.

    ..  container:: example

        Calling the object will return an ``abjad.Selection`` generated by
        the fading process. Each call of the object will apply the fading
        process to the previous result. By default, the container will be faded
        out (that is, its logical ties will be gradually removed one by one).

        >>> input_music = abjad.Container(r"c'4 ~ c'16 d'8. e'8 f'8 ~ f'4")
        >>> fader = auxjad.Fader(input_music)
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            ~
            c'16
            d'8.
            e'8
            f'8
            ~
            f'4
        }

        .. figure:: ../_images/image-Fader-1.png

        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            ~
            c'16
            r8.
            e'8
            f'8
            ~
            f'4
        }

        .. figure:: ../_images/image-Fader-2.png

        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            r2
            e'8
            f'8
            ~
            f'4
        }

        .. figure:: ../_images/image-Fader-3.png

        The property ``current_window`` can be used to access the current
        window without moving the head forwards.

        >>> notes = fader.current_window()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            r2
            e'8
            f'8
            ~
            f'4
        }

        .. figure:: ../_images/image-Fader-4.png

    ..  container:: example

        The very first call will output the input container without processing
        it. To disable this behaviour and apply the fading process on the very
        first call, initialise the class with the keyword argument
        ``fade_on_first_call`` set to ``True``.

        >>> input_music = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> fader = auxjad.Fader(input_music,
        ...                      fade_on_first_call=True,
        ...                      )
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'4
            e'4
            r4
        }

        .. figure:: ../_images/image-Fader-5.png

    ..  container:: example

        The fader can be of two types, either ``'in'`` or ``'out'`` defined by
        the keyword argument ``fader_type``. When it is set to ``'in'``, the
        fader will start with an empty container with the same length and time
        signature structure as the input music and will gradually add the
        original logical ties one by one.

        >>> input_music = abjad.Container(r"c'4 ~ c'16 d'8. e'8 f'8 ~ f'4")
        >>> fader = auxjad.Fader(input_music,
        ...                      fader_type='in',
        ...                      )
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            R1
        }

        .. figure:: ../_images/image-Fader-6.png

        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            r2
            r8
            f'8
            ~
            f'4
        }

        .. figure:: ../_images/image-Fader-7.png

        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            ~
            c'16
            r8.
            r8
            f'8
            ~
            f'4
        }

        .. figure:: ../_images/image-Fader-8.png

    ..  container:: example

        The property ``fader_type`` can also be changed after initialisation,
        as shown below.

        >>> input_music = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> fader = auxjad.Fader(input_music)
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-Fader-9.png

        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'4
            r4
            f'4
        }

        .. figure:: ../_images/image-Fader-10.png

        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'4
            r2
        }

        .. figure:: ../_images/image-Fader-11.png

        >>> fader.fader_type = 'in'
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'4
            e'4
            r4
        }

        .. figure:: ../_images/image-Fader-12.png

        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-Fader-13.png

    ..  container:: example

        The instances of ``Fader`` can also be used as an iterator,
        which can then be used in a for loop to run through the whole process.

        >>> input_music = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> fader = auxjad.Fader(input_music)
        >>> staff = abjad.Staff()
        >>> for notes in fader:
        ...     staff.append(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            d'4
            e'4
            f'4
            c'4
            r4
            e'4
            f'4
            r2
            e'4
            f'4
            r2
            e'4
            r4
            R1
        }

        .. figure:: ../_images/image-Fader-14.png

    ..  container:: example

        This class can take many optional keyword arguments during its
        creation, besides ``fader_type``. ``max_steps`` sets the maximum number
        of logical ties that can be faded in/out at each iteration, ranging
        between ``1`` and the input value (default is also ``1``). By default,
        calling the object in fade out mode will return the original container,
        and calling it in fade in mode will return a container filled with
        rests; set ``fade_on_first_call`` to ``True`` and the fade process will
        be applied on the very first call.  ``disable_rewrite_meter`` disables
        the ``rewrite_meter()`` mutation which is applied to the container
        after every call, and ``omit_all_time_signatures`` will remove all time
        signatures from the output (both are ``False`` by default). By default,
        the first time signature is attached only to the first leaf of the
        first call (unless time signature changes require it). To force every
        returned selection to start with a time signature attached to its first
        leaf, set ``force_time_signature`` to ``True``. Any measure filled with
        rests will be rewritten using a multi-measure rest; set the
        ``use_multimeasure_rest`` to ``False`` to disable this behaviour.
        Lastly, an initial mask for the logical ties can be set using ``mask``,
        which should be a ``list`` of the same length as the number of pitched
        logical ties in the input container. When ``fader_type`` is set to
        ``'out'``, the mask is initialised with ``1``'s, and when it is set to
        ``'in'``, it is initialised with ``0``'s. Change it to a mix of ``1``'s
        and ``0``'s to start the process with some specific logical ties
        already hidden/shown.

        >>> input_music = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> fader = auxjad.Fader(input_music,
        ...                      fader_type='in',
        ...                      max_steps=2,
        ...                      fade_on_first_call=True,
        ...                      disable_rewrite_meter=True,
        ...                      omit_all_time_signatures=True,
        ...                      force_time_signature=True,
        ...                      use_multimeasure_rest=False,
        ...                      mask=[1, 0, 1, 1, 0],
        ...                      )
        >>> fader.fader_type
        'in'
        >>> fader.max_steps
        2
        >>> fader.fade_on_first_call
        True
        >>> fader.disable_rewrite_meter
        True
        >>> fader.omit_all_time_signatures
        True
        >>> fader.force_time_signature
        True
        >>> fader.use_multimeasure_rest
        False
        >>> fader.mask
        [1, 0, 1, 1, 0]

        Use the properties below to change these values after initialisation.

        >>> fader.fader_type = 'out'
        >>> fader.max_steps = 1
        >>> fader.disable_rewrite_meter = False
        >>> fader.omit_all_time_signatures = False
        >>> fader.force_time_signature = False
        >>> fader.use_multimeasure_rest = True
        >>> fader.mask = [0, 1, 1, 0, 1]
        >>> fader.fader_type
        'out'
        >>> fader.max_steps
        1
        >>> fader.fade_on_first_call
        False
        >>> fader.disable_rewrite_meter
        False
        >>> fader.omit_all_time_signatures
        False
        >>> fader.force_time_signature
        False
        >>> fader.use_multimeasure_rest
        True
        >>> fader.mask
        [0, 1, 1, 0, 1]

    .. container:: example

        Use the ``contents`` property to read as well as overwrite the contents
        of the fader. Notice that ``mask`` will also be reset at that point.

        >>> input_music = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> fader = auxjad.Fader(input_music)
        >>> notes = fader()
        >>> fader.mask
        [1, 1, 1, 1]
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-Fader-15.png

        >>> notes = fader()
        >>> fader.mask
        [0, 1, 1, 1]
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            r4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-Fader-16.png

        >>> fader.contents = abjad.Container(r"c'16 d'16 e'16 f'16 g'2.")
        >>> fader.mask
        [1, 1, 1, 1, 1]
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'16
            d'16
            e'16
            f'16
            g'2.
        }

        .. figure:: ../_images/image-Fader-17.png

        >>> notes = fader()
        >>> fader.mask
        [1, 1, 1, 1, 1]
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'16
            d'16
            r16
            f'16
            g'2.
        }

        .. figure:: ../_images/image-Fader-18.png

    ..  container:: example

        To run through the whole process and output it as a single container,
        from the initial head position until the process outputs the single
        last element, use the method ``output_all()``.

        >>> input_music = abjad.Container(r"c'4. d'8 e'2")
        >>> fader = auxjad.Fader(input_music)
        >>> notes = fader.output_all()
        >>> staff = abjad.Staff(music)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            ~
            c'8
            d'8
            e'2
            r4
            r8
            d'8
            e'2
            r4
            r8
            d'8
            r2
            R1
        }

        .. figure:: ../_images/image-Fader-19.png

    ..  container:: example

        To run through just part of the process and output it as a single
        container, use the method``output_n()`` and pass the number of
        iterations as argument.

        >>> input_music = abjad.Container(r"c'4. d'8 e'16 f'16 g'4.")
        >>> fader = auxjad.Fader(input_music)
        >>> notes = fader.output_n(3)
        >>> staff = abjad.Staff(music)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            ~
            c'8
            d'8
            e'16
            f'16
            g'8
            ~
            g'4
            c'4
            ~
            c'8
            r8
            e'16
            f'16
            g'8
            ~
            g'4
            c'4
            ~
            c'8
            r8
            e'16
            f'16
            r8
            r4
        }

        .. figure:: ../_images/image-Fader-20.png

    ..  container:: example

        The function ``len()`` returns the number of pitched logical ties in
        ``contents``.

        >>> input_music = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> fader = auxjad.Fader(input_music)
        >>> len(fader)
        4
        >>> input_music = abjad.Container(r"<c' e' g'>4 d'4 <e' g' b'>4 f'4")
        >>> fader = auxjad.Fader(input_music)
        >>> len(fader)
        4
        >>> input_music = abjad.Container(r"c'4 ~ c'8 d'8 e'4 ~ e'8 f'8")
        >>> fader = auxjad.Fader(input_music)
        >>> len(fader)
        4
        >>> input_music = abjad.Container(r"c'4 ~ c'16 r16 d'8 "
        ...                               r"e'4 ~ e'8 f'16 r16")
        >>> fader = auxjad.Fader(input_music)
        >>> len(fader)
        4

    ..  container:: example

        Setting the keyword argument ``max_steps`` to a value larger than ``1``
        will result in a random number of steps (between ``1`` and
        ``max_steps``) being applied at each call.

        >>> input_music = abjad.Container(r"c'8 d'8 e'8 f'8 g'8 a'8 b'8 c''8")
        >>> fader = auxjad.Fader(input_music,
        ...                              max_steps=3,
        ...                              fade_on_first_call=True,
        ...                              )
        >>> notes = fader.output_n(3)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        \new Staff
        {
            c'8
            d'8
            r8
            f'8
            g'8
            a'8
            b'8
            c''8
            c'8
            r8
            r8
            f'8
            g'8
            a'8
            b'8
            r8
            r2
            g'8
            r8
            b'8
            r8
        }

        .. figure:: ../_images/image-Fader-21.png

    .. container:: example

        The property ``mask`` is used to represent whether each pitched logical
        tie is hidden or shown. It is a ``list`` of the same length as the
        number of pitched logical ties in the input container. When
        ``fader_type`` is set to ``'out'``, the mask is initialised with
        ``1``'s, and when it is set to ``'in'``, it is initialised with
        ``0``'s. Change it to a mix of ``1``'s and ``0``'s to start the process
        with some logical ties already hidden/shown. Use the method
        ``reset_mask()`` to reset it back to its default value (depending on
        ``fader_type``).

        >>> input_music = abjad.Container(r"c'4 d'8 e'8 f'4 ~ f'8. g'16")
        >>> fader = auxjad.Fader(input_music)
        >>> fader.mask
        [1, 1, 1, 1, 1]
        >>> fader = auxjad.Fader(input_music,
        ...                      fader_type='in',
        ...                      )
        >>> fader.mask
        [0, 0, 0, 0, 0]
        >>> for _ in range(3):
        ...     fader()
        ...     fader.mask
        [0, 0, 0, 0, 0]
        [0, 1, 0, 0, 0]
        [0, 1, 1, 0, 0]
        >>> staff = abjad.Staff(fader.current_window)
        >>> abjad.f(staff)
        \new Staff
        {
            r4
            d'8
            e'8
            r2
        }

        .. figure:: ../_images/image-Fader-22.png

        >>> fader.mask = [1, 0, 1, 1, 0]
        >>> fader.mask
        [1, 0, 1, 1, 0]
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            r8
            e'8
            f'4
            ~
            f'8.
            r16
        }

        .. figure:: ../_images/image-Fader-23.png

        >>> fader.reset_mask()
        >>> fader.mask
        [0, 0, 0, 0, 0]
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            R1
        }

        .. figure:: ../_images/image-Fader-24.png


    .. container:: example

        By default, all rests in a measure filled only with rests will be
        converted into a multi-measure rest. Set ``use_multimeasure_rest`` to
        ``False`` to disable this. Also, by default, all output is mutated
        through abjad's ``rewrite_meter()``. To disable it, set
        ``disable_rewrite_meter`` to ``True``.

        >>> input_music = abjad.Container(r"c'8 d'8 e'2.")
        >>> fader = auxjad.Fader(input_music,
        ...                      disable_rewrite_meter=True,
        ...                      use_multimeasure_rest=False,
        ...                      )
        >>> notes = fader.output_all()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'8
            d'8
            e'2.
            c'8
            r8
            e'2.
            c'8
            r8
            r2.
            r8
            r8
            r2.
        }

        .. figure:: ../_images/image-Fader-25.png

    .. container:: example

        To disable time signatures altogether, initialise this class with the
        keyword argument ``omit_all_time_signatures`` set to ``True`` (default
        is ``False``), or use the ``omit_all_time_signatures`` property after
        initialisation.

        >>> input_music = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> fader = auxjad.Fader(input_music,
        ...                      omit_all_time_signatures=True,
        ...                      )
        >>> notes = fader()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'2
            e'4
        }

        .. figure:: ../_images/image-Fader-26.png

    ..  container:: example

        By default, only the first output bar will contain a time signature,
        and all subsequent bars won't have one. Use the optional keyword
        argument ``force_time_signature`` when inisialising the object, or
        alternatively set the property of the same name, to change this
        behaviour. Compare the two cases below; in the first, the variable
        ``notes2`` won't have a time signature appended to its first leaf
        because the fader had been called before (though LilyPond will
        fallback to a default 4/4 time signature when none is found in the
        source file). In the second, ``force_time_signature`` is set to
        ``True``, and the output of ``abjad.f(staff)`` now includes
        ``\time 3/4`` (and LilyPond does not fallback to a 4/4 time signature).

        >>> input_music = abjad.Container(r"\time 3/4 c'4 d'4 e'4")
        >>> fader = auxjad.Fader(input_music)
        >>> notes1 = fader()
        >>> notes2 = fader()
        >>> staff = abjad.Staff(notes2)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            r4
            e'4
        }

        .. figure:: ../_images/image-Fader-27.png

        >>> input_music = abjad.Container(r"\time 3/4 c'4 d'4 e'4")
        >>> fader = auxjad.Fader(input_music,
        ...                      force_time_signature=True,
        ...                      )
        >>> notes1 = fader()
        >>> notes2 = fader()
        >>> staff = abjad.Staff(notes2)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            r4
            e'4
        }

        .. figure:: ../_images/image-Fader-28.png

    ..  container:: example

        This class can handle dynamics and articulations too. Hairpins might
        need manual tweaking if the leaf under which they terminate is removed.

        >>> input_music = abjad.Container(
        ...     r"\time 3/4 <e' g' b'>8->\f d'8\p ~ d'4 f'8..-- g'32-.")
        >>> fader = auxjad.Fader(input_music)
        >>> notes = fader.output_all()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            <e' g' b'>8
            \f
            - \accent
            d'8
            \p
            ~
            d'4
            f'8..
            - \tenuto
            g'32
            - \staccato
            <e' g' b'>8
            \f
            - \accent
            d'8
            \p
            ~
            d'4
            r8..
            g'32
            - \staccato
            <e' g' b'>8
            \f
            - \accent
            r8
            r4
            r8..
            g'32
            - \staccato
            <e' g' b'>8
            \f
            - \accent
            r8
            r2
            R1 * 3/4
        }

        .. figure:: ../_images/image-Fader-29.png

    ..  container:: example

        This class can handle tuplets.

        >>> input_music = abjad.Container(r"\times 2/3 {c'8 d'8 e'8} d'2.")
        >>> fader = auxjad.Fader(input_music)
        >>> notes = fader.output_all()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \times 2/3 {
                \time 4/4
                c'8
                d'8
                e'8
            }
            d'2.
            \times 2/3 {
                r8
                d'8
                e'8
            }
            d'2.
            \times 2/3 {
                r8
                d'8
                r8
            }
            d'2.
            \times 2/3 {
                r8
                d'8
                r8
            }
            r2.
            R1
        }

        .. figure:: ../_images/image-Fader-30.png
    """

    ### CLASS VARIABLES ###

    __slots__ = ('_contents',
                 '_current_window',
                 '_fader_type',
                 '_max_steps',
                 '_disable_rewrite_meter',
                 '_mask',
                 '_is_first_window',
                 '_time_signatures',
                 '_omit_all_time_signatures',
                 '_force_time_signature',
                 '_use_multimeasure_rest',
                 '_new_mask',
                 )

    ### INITIALISER ###

    def __init__(self,
                 contents: abjad.Container,
                 *,
                 fader_type: str = 'out',
                 max_steps: int = 1,
                 fade_on_first_call: bool = False,
                 disable_rewrite_meter: bool = False,
                 omit_all_time_signatures: bool = False,
                 force_time_signature: bool = False,
                 use_multimeasure_rest: bool = True,
                 mask: list = None,
                 ):
        r'Initialises self.'
        self.fader_type = fader_type
        self.max_steps = max_steps
        self.contents = contents
        if not isinstance(fade_on_first_call, bool):
            raise TypeError("'fade_on_first_call' must be 'bool'")
        self.disable_rewrite_meter = disable_rewrite_meter
        self.omit_all_time_signatures = omit_all_time_signatures
        self.force_time_signature = force_time_signature
        self.use_multimeasure_rest = use_multimeasure_rest
        if mask:
            self.mask = mask
        self._is_first_window = not fade_on_first_call
        self._current_window = None
        self._new_mask = False

    ### SPECIAL METHODS ###

    def __repr__(self) -> str:
        r'Returns interpret representation of  ``contents``.'
        return format(self._contents)

    def __len__(self) -> int:
        r'Returns the number of logical ties ``contents``.'
        return len(abjad.select(self._contents).logical_ties(pitched=True))

    def __call__(self) -> abjad.Selection:
        r"""Calls the fading process for one iteration, returning an
        ``abjad.Selection``.
        """
        if not self._is_first_window and not self._new_mask:
            if self._fader_type == 'out':
                self._remove_element()
            else:
                self._add_element()
            self._mask_to_selection()
        else:
            self._mask_to_selection()
            self._is_first_window = False
            self._new_mask = False
        return copy.deepcopy(self._current_window)

    def __next__(self) -> abjad.Selection:
        r"""Calls the fading process for one iteration, returning an
        ``abjad.Selection``.
        """
        if self._done:
            raise StopIteration
        if not self._is_first_window and not self._new_mask:
            if self._fader_type == 'out':
                self._remove_element()
            else:
                self._add_element()
            self._mask_to_selection()
        else:
            self._mask_to_selection()
            self._is_first_window = False
            self._new_mask = False
        return copy.deepcopy(self._current_window)

    def __iter__(self):
        r'Returns an iterator, allowing instances to be used as iterators.'
        return self

    ### PUBLIC METHODS ###

    def output_all(self) -> abjad.Selection:
        r"""Goes through the whole fading process and outputs a single
        ``abjad.Selection``.
        """
        dummy_container = abjad.Container()
        while True:
            dummy_container.append(self.__call__())
            if self._done:
                break
        result = dummy_container[:]
        dummy_container[:] = []
        return result

    def output_n(self,
                 n: int,
                 ) -> abjad.Selection:
        r"""Goes through ``n`` iterations of the fading process and outputs a
        single ``abjad.Selection``.
        """
        if not isinstance(n, int):
            raise TypeError("first positional argument must be 'int'")
        if n < 1:
            raise ValueError("first positional argument must be a positive "
                             "'int'")
        dummy_container = abjad.Container()
        for _ in range(n):
            dummy_container.append(self.__call__())
        result = dummy_container[:]
        dummy_container[:] = []
        return result

    def reset_mask(self):
        r'Creates a mask filled with a default value for the logical ties.'
        self._new_mask = True
        if self._fader_type == 'out':
            self._mask = [1 for _ in range(self.__len__())]
        else:
            self._mask = [0 for _ in range(self.__len__())]

    ### PRIVATE METHODS ###

    def _remove_element(self):
        r'Sets a random element of the mask to ``False``.'
        for _ in range(random.randint(1, self._max_steps)):
            if 1 in self._mask:
                while True:
                    index = random.randint(0, self.__len__() - 1)
                    if self._mask[index] == 1:
                        self._mask[index] = 0
                        break
            else:
                raise RuntimeError("'current_window' is already empty")

    def _add_element(self):
        r'Sets a random element of the mask to ``True``.'
        for _ in range(random.randint(1, self._max_steps)):
            if 0 in self._mask:
                while True:
                    index = random.randint(0, self.__len__() - 1)
                    if self._mask[index] == 0:
                        self._mask[index] = 1
                        break
            else:
                raise RuntimeError("'current_window' is already full")

    def _mask_to_selection(self):
        r'Applies the mask to the current window.'
        dummy_container = copy.deepcopy(self._contents)
        logical_ties = abjad.select(dummy_container).logical_ties(pitched=True)
        for mask_value, logical_tie in zip(self._mask, logical_ties):
            if mask_value == 0:
                for leaf in logical_tie:
                    abjad.mutate(leaf).replace(
                        abjad.Rest(leaf.written_duration))
        if not self.omit_all_time_signatures:
            # applying time signatures and rewrite meter
            enforce_time_signature(
                dummy_container,
                self._time_signatures,
                disable_rewrite_meter=self._disable_rewrite_meter,
            )
            if self._use_multimeasure_rest:
                rests_to_multimeasure_rest(dummy_container)
            if not self._is_first_window and not self._force_time_signature:
                if self._time_signatures[0] == self._time_signatures[-1]:
                    abjad.detach(abjad.TimeSignature,
                                 abjad.select(dummy_container).leaf(0),
                                 )
        else:
            for logical_tie in logical_ties:
                for leaf in logical_tie:
                    if abjad.inspect(leaf).indicator(abjad.TimeSignature):
                        abjad.detach(abjad.TimeSignature, leaf)
        # output
        self._current_window = dummy_container[:]
        dummy_container[:] = []

    ### PUBLIC PROPERTIES ###

    @property
    def contents(self) -> abjad.Container:
        r'The ``abjad.Container`` to be faded.'
        return copy.deepcopy(self._contents)

    @contents.setter
    def contents(self,
                 contents: abjad.Container,
                 ):
        if not isinstance(contents, abjad.Container):
            raise TypeError("'contents' must be 'abjad.Container' or "
                            "child class")
        self._contents = copy.deepcopy(contents)
        self._time_signatures = time_signature_extractor(contents,
                                                         do_not_use_none=True,
                                                         )
        self.reset_mask()

    @property
    def current_window(self) -> abjad.Selection:
        r'Read-only property, returns the previously output selection.'
        return copy.deepcopy(self._current_window)

    @property
    def fader_type(self) -> str:
        r"Type of fading, must be either ``'in'`` or ``'out'``."
        return self._fader_type

    @fader_type.setter
    def fader_type(self,
                   fader_type: str,
                   ):
        if not isinstance(fader_type, str):
            raise TypeError("'fader_type' must be 'str'")
        if fader_type not in ('in', 'out'):
            raise ValueError("'fader_type' must be either 'in' or 'out'")
        self._fader_type = fader_type

    @property
    def max_steps(self) -> int:
        r'The maximum number of steps per operation.'
        return self._max_steps

    @max_steps.setter
    def max_steps(self,
                  max_steps: int,
                  ):
        if not isinstance(max_steps, int):
            raise TypeError("'max_steps' must be 'int'")
        if max_steps < 1:
            raise ValueError("'max_steps' must be greater than zero")
        self._max_steps = max_steps

    @property
    def mask(self) -> list:
        r"Mask with ``1``'s and ``0``'s representing the logical ties.'"
        return self._mask

    @mask.setter
    def mask(self,
             mask: list,
             ):
        if not isinstance(mask, list):
            raise TypeError("'mask' must be 'list'")
        if any(element not in (0, 1) for element in mask):
            raise ValueError("'mask' must contain only 1's and 0's")
        if len(mask) != self.__len__():
            raise ValueError("'mask' must have the same length as the number "
                             "of logical ties in 'contents'")
        self._mask = mask
        self._new_mask = True

    @property
    def disable_rewrite_meter(self) -> bool:
        r"""When ``True``, the durations of the notes in the output will not be
        rewritten by the ``rewrite_meter`` mutation.
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
    def omit_all_time_signatures(self) -> bool:
        r'When ``True``, all time signatures will be omitted from the output.'
        return self._omit_all_time_signatures

    @omit_all_time_signatures.setter
    def omit_all_time_signatures(self,
                                 omit_all_time_signatures: bool,
                                 ):
        if not isinstance(omit_all_time_signatures, bool):
            raise TypeError("'omit_all_time_signatures' must be 'bool'")
        self._omit_all_time_signatures = omit_all_time_signatures

    @property
    def force_time_signature(self) -> bool:
        r"""When ``True``, the initial time signature of a window is always
        attached to the first leaf.
        """
        return self._force_time_signature

    @force_time_signature.setter
    def force_time_signature(self,
                             force_time_signature: bool,
                             ):
        if not isinstance(force_time_signature, bool):
            raise TypeError("'force_time_signature' must be 'bool'")
        self._force_time_signature = force_time_signature

    @property
    def use_multimeasure_rest(self) -> bool:
        r'When ``True``, multimeasure rests will be used for silent measures.'
        return self._use_multimeasure_rest

    @use_multimeasure_rest.setter
    def use_multimeasure_rest(self,
                              use_multimeasure_rest: bool,
                              ):
        if not isinstance(use_multimeasure_rest, bool):
            raise TypeError("'use_multimeasure_rest' must be 'bool'")
        self._use_multimeasure_rest = use_multimeasure_rest

    ### PRIVATE PROPERTIES ###

    @property
    def _done(self) -> bool:
        r"""Boolean indicating whether the process is done, which is when the
        mask is filled with ``1``'s with ``fader_type`` set to ``'in'`` or when
        the mask is filled with ``0``'s with ``fader_type`` set to ``'out'``.
        """
        if self._fader_type == 'out':
            return 1 not in self._mask
        else:
            return 0 not in self._mask
