import copy
from math import ceil
from typing import Optional, Union

import abjad

from ._LooperParent import _LooperParent


class WindowLooper(_LooperParent):
    r"""``WindowLooper`` outputs slices of an ``abjad.Container`` using the
    metaphor of a looping window of a constant size (given by an
    ``abjad.Duration``).

    Example:
        Calling the object will return an ``abjad.Selection`` generated by the
        looping process. Each call of the object will move the window forwards
        and output the sliced window. If no ``window_size`` nor ``step_size``
        are entered as arguments, they are set to the following default values,
        respectively: (4, 4), i.e. a window of the size of a 4/4 bar, and
        (1, 16), i.e. a step of the length of a sixteenth-note.

        >>> container = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> looper = auxjad.WindowLooper(container)
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            d'2
            e'4
        }

        .. figure:: ../_images/image-WindowLooper-1.png

        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'8.
            d'16
            ~
            d'4..
            e'16
            ~
            e'8.
            f'16
        }

        .. figure:: ../_images/image-WindowLooper-2.png

        The property ``current_window`` can be used to access the current
        window without moving the head forwards.

        >>> notes = looper.current_window()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'8.
            d'16
            ~
            d'4..
            e'16
            ~
            e'8.
            f'16
        }

        .. figure:: ../_images/image-WindowLooper-3.png

    Example:
        The very first call will output the input container without processing
        it. To disable this behaviour and have the looping window move on the
        very first call, initialise the class with the keyword argument
        ``processs_on_first_call`` set to ``True``.

        >>> container = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> looper = auxjad.WindowLooper(container,
        ...                              processs_on_first_call=True,
        ...                              )
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'8.
            d'16
            ~
            d'4..
            e'16
            ~
            e'8.
            f'16
        }

        .. figure:: ../_images/image-WindowLooper-4.png

    Example:
        The optional arguments ``window_size`` and ``step_size`` can be used to
        set different window and step sizes. ``window_size`` can take a tuple
        or an ``abjad.Meter`` as input, while ``step_size`` takes a tuple or an
        ``abjad.Duration``.

        >>> container = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 8),
        ...                              )
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            d'2
        }

        .. figure:: ../_images/image-WindowLooper-5.png

        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'8
            d'8
            ~
            d'4.
            e'8
        }

        .. figure:: ../_images/image-WindowLooper-6.png

    Example:
        The instances of ``WindowLooper`` can also be used as an iterator,
        which can then be used in a for loop to exhaust all windows. Notice how
        it appends rests at the end of the container, until it is totally
        exhausted. Note that unlike the methods ``output_n()`` and
        ``output_all()``, time signatures are added to each window returned by
        the shuffler. Use the function
        ``auxjad.remove_repeated_time_signatures()`` to clean the output when
        using ``WindowLooper`` in this way.

        >>> container = abjad.Container(r"c'4 d'2 e'4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 8),
        ...                              )
        >>> staff = abjad.Staff()
        >>> for window in looper:
        ...     staff.append(window)
        >>> auxjad.remove_repeated_time_signatures(staff)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            d'2
            c'8
            d'8
            ~
            d'4.
            e'8
            d'2
            e'4
            d'4.
            e'8
            ~
            e'8
            r8
            d'4
            e'4
            r4
            d'8
            e'8
            ~
            e'8
            r4.
            e'4
            r2
            e'8
            r8
            r2
        }

        .. figure:: ../_images/image-WindowLooper-7.png

    Example:
        In order to stop the process when the end of the looping window matches
        the end of the ``contents`` (and thus appending rests to the output),
        set the optional keyword argument ``fill_with_rests`` to ``True``.
        Compare the two approaches below.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 4),
        ...                              )
        >>> staff = abjad.Staff()
        >>> for window in looper:
        ...     staff.append(window)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            d'4
            e'4
            d'4
            e'4
            f'4
            e'4
            f'4
            r4
            f'4
            r2
        }

        .. figure:: ../_images/image-WindowLooper-8.png

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 4),
        ...                              fill_with_rests=False,
        ...                              )
        >>> staff = abjad.Staff()
        >>> for window in looper:
        ...     staff.append(window)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            d'4
            e'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-WindowLooper-9.png

    Example:
        This class can take many optional keyword arguments during its
        creation, besides ``window_size`` and ``step_size``. ``max_steps`` sets
        the maximum number of steps that the window can advance when the object
        is called, ranging between ``1`` and the input value (default is also
        ``1``). ``repetition_chance`` sets the chance of a window result
        repeating itself (that is, the window not moving forwards when called).
        It should range from ``0.0`` to ``1.0`` (default ``0.0``, i.e. no
        repetition). ``forward_bias`` sets the chance of the window moving
        forward instead of backwards. It should range from ``0.0`` to ``1.0``
        (default ``1.0``, which means the window can only move forwards. A
        value of ``0.5`` gives 50% chance of moving forwards while a value of
        ``0.0`` will move the window only backwards). ``head_position`` can be
        used to offset the starting position of the  looping window. It must be
        a tuple or an ``abjad.Duration``, and its default value is ``0``. The
        properties ``boundary_depth``, ``maximum_dot_count``, and
        ``rewrite_tuplets`` are passed as arguments to abjad's
        ``rewrite_meter()``, see its documentation for more information. By
        default, calling the object will first return the original container
        and subsequent  calls will process it; set ``processs_on_first_call``
        to ``True`` and the looping process will be applied on the very first
        call.

        >>> container = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(5, 8),
        ...                              max_steps=2,
        ...                              repetition_chance=0.25,
        ...                              forward_bias=0.2,
        ...                              head_position=(2, 8),
        ...                              omit_time_signatures=False,
        ...                              fill_with_rests=False,
        ...                              boundary_depth=0,
        ...                              maximum_dot_count=1,
        ...                              rewrite_tuplets=False,
        ...                              processs_on_first_call=True,
        ...                              )
        >>> looper.window_size
        3/4
        >>> looper.step_size
        5/8
        >>> looper.repetition_chance
        0.25
        >>> looper.forward_bias
        0.2
        >>> looper.max_steps
        2
        >>> looper.head_position
        1/4
        >>> looper.omit_time_signatures
        False
        >>> looper.fill_with_rests
        False
        >>> looper.boundary_depth
        0
        >>> looper.maximum_dot_count
        1
        >>> looper.rewrite_tuplets
        False
        >>> looper.boundary_depth
        0
        >>> looper.maximum_dot_count
        1
        >>> looper.rewrite_tuplets
        False
        >>> looper.processs_on_first_call
        True

        Use the properties below to change these values after initialisation.

        >>> looper.window_size = (5, 4)
        >>> looper.step_size = (1, 4)
        >>> looper.max_steps = 3
        >>> looper.repetition_chance = 0.1
        >>> looper.forward_bias = 0.8
        >>> looper.head_position = 0
        >>> looper.omit_time_signatures = True
        >>> looper.boundary_depth = 1
        >>> looper.maximum_dot_count = 2
        >>> looper.rewrite_tuplets = True
        >>> looper.processs_on_first_call = False
        >>> looper.window_size
        5/4
        >>> looper.step_size
        1/4
        >>> looper.max_steps
        3
        >>> looper.repetition_chance
        0.1
        >>> looper.forward_bias
        0.8
        >>> looper.head_position
        0
        >>> looper.omit_time_signatures
        True
        >>> looper.boundary_depth
        1
        >>> looper.maximum_dot_count
        2
        >>> looper.rewrite_tuplets
        True
        >>> looper.processs_on_first_call
        False

    Example:
        Set ``forward_bias`` to ``0.0`` to move backwards instead of forwards
        (default is ``1.0``). The initial ``head_position`` must be greater
        than ``0`` otherwise the contents will already be exhausted in the very
        first call (since it will not be able to move backwards from that
        position).

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4 g'4 a'4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 4),
        ...                              head_position=(3, 4),
        ...                              forward_bias=0.0,
        ...                              )
        >>> notes = looper.output_n(3)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            f'4
            g'4
            a'4
            e'4
            f'4
            g'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-WindowLooper-10.png

    Example:
        Setingt ``forward_bias`` to a value in between ``0.0`` and ``1.0`` will
        result in random steps being taken forward or backward, according to
        the bias. The initial value of ``head_position`` will once gain play
        an important role here, as the contents might be exhausted if the
        looper attempts to move backwards after reaching the head position
        ``0``.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4 g'4 a'4 b'4 c''4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 4),
        ...                              head_position=(3, 4),
        ...                              forward_bias=0.5,
        ...                              )
        >>> notes = looper.output_n(5)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            f'4
            g'4
            a'4
            e'4
            f'4
            g'4
            d'4
            e'4
            f'4
            e'4
            f'4
            g'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-WindowLooper-11.png

    Example:
        Setting the keyword argument ``max_steps`` to a value larger than ``1``
        will result in a random number of steps (between ``1`` and
        ``max_steps``) being applied at each call.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4 g'4 a'4 b'4 c''4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(1, 4),
        ...                              step_size=(1, 4),
        ...                              max_steps=4,
        ...                              )
        >>> notes = looper.output_n(4)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 1/4
            c'4
            f'4
            b'4
            c''4
        }

        .. figure:: ../_images/image-WindowLooper-12.png

    Example:
        The function ``len()`` can be used to get the total number of steps
        in the contents (always rounded up).

        >>> container = abjad.Container(r"c'1")
        >>> looper = auxjad.WindowLooper(container)
        >>> len(looper)
        16
        >>> container = abjad.Container(r"c'1")
        >>> looper = auxjad.WindowLooper(container,
        ...                              step_size=(1, 4),
        ...                              )
        >>> len(looper)
        4
        >>> container = abjad.Container(r"c'2..")
        >>> looper = auxjad.WindowLooper(container,
        ...                              step_size=(1, 4),
        ...                              window_size=(2, 4),
        ...                              )
        >>> len(looper)
        4

    Example:
        To run through the whole process and output it as a single container,
        from the initial head position until the process outputs the single
        last element, use the method ``output_all()``. As shown above, set the
        optional keyword argument ``fill_with_rests`` to ``False`` if the
        process is to be stopped when the end of the looping window reaches the
        end of the contents (thus not appending rests).

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 4),
        ...                              )
        >>> notes = looper.output_all()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            d'4
            e'4
            d'4
            e'4
            f'4
            e'4
            f'4
            r4
            f'4
            r2
        }

        .. figure:: ../_images/image-WindowLooper-13.png

    Example:
        When using ``output_all()``, set the keyword argument
        ``tie_identical_pitches`` to ``True`` in order to tie identical notes
        or chords at the end and beginning of consecutive windows.

        >>> container = abjad.Container(r"c'4 <e' f' g'>2 r4 f'2.")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 4),
        ...                              )
        >>> notes = looper.output_all(tie_identical_pitches=True)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            <e' f' g'>2
            ~
            <e' f' g'>2
            r4
            <e' f' g'>4
            r4
            f'4
            r4
            f'2
            ~
            f'2.
            ~
            f'2
            r4
            f'4
            r2
        }

        .. figure:: ../_images/image-WindowLooper-14.png

    Example:
        To run through just part of the process and output it as a single
        container, starting from the initial head position, use the method
        ``output_n()`` and pass the number of iterations as argument. Similarly
        to ``output_all()``, the optional keyword arguments
        ``tie_identical_pitches`` and ``fill_with_rests`` are available.

        >>> container = abjad.Container(r"c'4 d'4 e'4 f'4")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 4),
        ...                              )
        >>> notes = looper.output_n(2)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/4
            c'4
            d'4
            e'4
            d'4
            e'4
            f'4
        }

        .. figure:: ../_images/image-WindowLooper-15.png

    Example:
        To change the size of the looping window after instantiation, use the
        property ``window_size``. In the example below, the initial window is
        of size (4, 4), but changes to (3, 8) after three calls.

        >>> container = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> looper = auxjad.WindowLooper(container)
        >>> notes = looper.output_n(3)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            d'2
            e'4
            c'8.
            d'16
            ~
            d'4..
            e'16
            ~
            e'8.
            f'16
            c'8
            d'8
            ~
            d'4.
            e'8
            ~
            e'8
            f'8
        }

        .. figure:: ../_images/image-WindowLooper-16.png

        >>> looper.window_size = (3, 8)
        >>> notes = looper.output_n(3)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 3/8
            c'16
            d'16
            ~
            d'4
            d'4.
            d'4.
        }

        .. figure:: ../_images/image-WindowLooper-17.png

    Example:
        To disable time signatures altogether, initialise ``WindowLooper`` with
        the keyword argument ``omit_time_signatures`` set to ``True`` (default
        is ``False``), or use the ``omit_time_signatures`` property after
        initialisation.

        >>> container = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> looper = auxjad.WindowLooper(container,
        ...                              omit_time_signatures=True,
        ...                              )
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            c'4
            d'2
            e'4
        }

        .. figure:: ../_images/image-WindowLooper-18.png

    ..  tip::

        All methods that return an ``abjad.Selection`` will add an initial time
        signature to it. The ``output_n()`` and ``output_all()`` methods
        automatically remove repeated time signatures. When joining selections
        output by multiple method calls, use
        ``auxjad.remove_repeated_time_signatures()`` on the whole container
        after fusing the selections to remove any unecessary time signature
        changes.

    Example:
        This class can handle dynamics and articulations too. When a leaf is
        shortened by the looping window's movement, the dynamics and
        articulations are still applied to it.

        >>> container = abjad.Container(
        ...     r"c'4-.\p\< d'2--\f e'4->\ppp f'2 ~ f'8")
        >>> looper = auxjad.WindowLooper(container)
        >>> notes = looper.output_n(2)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            \p
            - \staccato
            \<
            d'2
            \f
            - \tenuto
            e'4
            \ppp
            - \accent
            c'8.
            \p
            - \staccato
            \<
            d'16
            \f
            - \tenuto
            ~
            d'4..
            e'16
            \ppp
            - \accent
            ~
            e'8.
            f'16
        }

        .. figure:: ../_images/image-WindowLooper-19.png

    .. tip::

        The functions ``auxjad.remove_repeated_dynamics()`` and
        ``auxjad.reposition_clefs()`` can be used to clean the output and
        remove repeated dynamics and unnecessary clef changes.

    ..  warning::

        Do note that elements that span multiple notes (such as hairpins,
        ottava indicators, manual beams, etc.) can become problematic when
        notes containing them are split into two. As a rule of thumb, it is
        always better to attach those to the music after the looping process
        has ended.

    Example:
        Use the ``contents`` property to read as well as overwrite the contents
        of the looper. Notice that the ``head_position`` will remain on its
        previous value and must be reset to ``0`` if that's required.

        >>> container = abjad.Container(r"c'4 d'2 e'4 f'2 ~ f'8 g'1")
        >>> looper = auxjad.WindowLooper(container)
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            d'2
            e'4
        }

        .. figure:: ../_images/image-WindowLooper-20.png

        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'8.
            d'16
            ~
            d'4..
            e'16
            ~
            e'8.
            f'16
        }

        .. figure:: ../_images/image-WindowLooper-21.png

        >>> looper.contents = abjad.Container(r"c'16 d'16 e'16 f'16 g'2. a'1")
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            d'16
            e'16
            f'16
            g'16
            ~
            g'2
            ~
            g'8.
            a'16
        }

        .. figure:: ../_images/image-WindowLooper-22.png

        >>> looper.head_position = 0
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'16
            d'16
            e'16
            f'16
            g'2.
        }

        .. figure:: ../_images/image-WindowLooper-23.png

    Example:
        This function uses the default logical tie splitting algorithm from
        abjad's ``rewrite_meter()``.

        >>> container = abjad.Container(r"c'4. d'8 e'2")
        >>> looper = auxjad.WindowLooper(container)
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4.
            d'8
            e'2
        }

        .. figure:: ../_images/image-WindowLooper-24.png

        Set ``boundary_depth`` to a different number to change its behaviour.

        >>> looper = auxjad.WindowLooper(container,
        ...                              boundary_depth=1,
        ...                              )
        >>> notes = looper()
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \time 4/4
            c'4
            ~
            c'8
            d'8
            e'2
        }

        .. figure:: ../_images/image-WindowLooper-25.png

        Other arguments available for tweaking the output of abjad's
        ``rewrite_meter()`` are ``maximum_dot_count`` and ``rewrite_tuplets``,
        which work exactly as the identically named arguments of
        ``rewrite_meter()``.

    ..  warning::

        This class can handle tuplets, but the output is often quite complex.
        Although the result will be rhythmically correct, consecutive tuplets
        are not fused together, and tuplets may be output off-beat. This
        functionality should be considered experimental.

        >>> container = abjad.Container(r"\times 2/3 {c'8 d'8 e'8} d'2.")
        >>> looper = auxjad.WindowLooper(container,
        ...                              window_size=(3, 4),
        ...                              step_size=(1, 16))
        >>> notes = looper.output_n(3)
        >>> staff = abjad.Staff(notes)
        >>> abjad.f(staff)
        \new Staff
        {
            \times 2/3 {
                \time 3/4
                c'8
                d'8
                e'8
            }
            d'2
            \times 2/3 {
                c'32
                d'16
                ~
                d'16
                e'8
            }
            d'16
            ~
            d'2
            \times 2/3 {
                d'16
                e'8
            }
            d'8
            ~
            d'2
        }

        .. figure:: ../_images/image-WindowLooper-26.png
    """

    ### CLASS VARIABLES ###

    __slots__ = ('_omit_time_signatures',
                 '_fill_with_rests',
                 '_contents_length',
                 '_contents_no_time_signature',
                 '_boundary_depth',
                 '_maximum_dot_count',
                 '_rewrite_tuplets',
                 )

    ### INITIALISER ###

    def __init__(self,
                 contents: abjad.Container,
                 *,
                 window_size: Union[tuple, abjad.Meter] = (4, 4),
                 step_size: Union[int,
                                  float,
                                  tuple,
                                  str,
                                  abjad.Duration,
                                  ] = (1, 16),
                 max_steps: int = 1,
                 repetition_chance: float = 0.0,
                 forward_bias: float = 1.0,
                 head_position: Union[int,
                                      float,
                                      tuple,
                                      str,
                                      abjad.Duration,
                                      ] = 0,
                 omit_time_signatures: bool = False,
                 processs_on_first_call: bool = False,
                 fill_with_rests: bool = True,
                 boundary_depth: Optional[int] = None,
                 maximum_dot_count: Optional[int] = None,
                 rewrite_tuplets: bool = True,
                 ):
        r'Initialises self.'
        self.contents = contents
        self.omit_time_signatures = omit_time_signatures
        self.fill_with_rests = fill_with_rests
        self.boundary_depth = boundary_depth
        self.maximum_dot_count = maximum_dot_count
        self.rewrite_tuplets = rewrite_tuplets
        super().__init__(head_position,
                         window_size,
                         step_size,
                         max_steps,
                         repetition_chance,
                         forward_bias,
                         processs_on_first_call,
                         )

    ### SPECIAL METHODS ###

    def __repr__(self) -> str:
        r'Returns interpret representation of  ``contents``.'
        return format(self._contents)

    def __len__(self) -> int:
        r'Returns the length of ``contents`` in terms of ``step_size``.'
        return ceil(self._contents_length / self._step_size)

    def __call__(self) -> abjad.Selection:
        r"""Calls the looping process for one iteration, returning an
        ``abjad.Selection``.
        """
        return super().__call__()

    def __next__(self) -> abjad.Selection:
        r"""Calls the looping process for one iteration, returning an
        ``abjad.Selection``.
        """
        return super().__next__()

    ### PRIVATE METHODS ###

    def _slice_contents(self):
        r"""This method takes a slice of size ``window_size`` out of the
        ``contents`` starting at the current ``head_position``.
        """
        head = self._head_position
        window_size = self._window_size
        dummy_container = copy.deepcopy(self._contents_no_time_signature)
        # splitting leaves at both slicing points
        if head > abjad.Duration(0):
            abjad.mutate(dummy_container[:]).split([head,
                                                    window_size.duration,
                                                    ])
        else:
            abjad.mutate(dummy_container[:]).split([window_size.duration])
        # finding start and end indeces for the window
        for start in range(len(dummy_container)):
            if abjad.inspect(dummy_container[:start + 1]).duration() > head:
                break
        for end in range(start + 1, len(dummy_container)):
            if (abjad.inspect(dummy_container[start : end]).duration()
                    == window_size.duration):
                break
        else:
            end = len(dummy_container)
        # passing on indicators from the head of an initial splitted leaf
        for index in range(start - 1, -1, -1):
            if abjad.inspect(dummy_container[index]).indicator(abjad.Tie):
                inspect_contents = abjad.inspect(dummy_container[index - 1])
                if index == 0 or not inspect_contents.indicator(abjad.Tie):
                    inspect_contents = abjad.inspect(dummy_container[index])
                    for indicator in inspect_contents.indicators():
                        if not isinstance(indicator,
                                          (abjad.TimeSignature, abjad.Tie),
                                          ):
                            abjad.attach(indicator, dummy_container[start])
        # removing ties generated by the split mutation
        abjad.detach(abjad.Tie(), dummy_container[start - 1])
        abjad.detach(abjad.Tie(), dummy_container[end - 1])
        # appending rests if necessary
        contents_dur = abjad.inspect(dummy_container[start : end]).duration()
        if contents_dur < window_size.duration:
            missing_dur = window_size.duration - contents_dur
            rests = abjad.LeafMaker()(None, missing_dur)
            dummy_container.extend(rests)
            end += len(rests)
        # transforming abjad.Selection -> abjad.Container for rewrite_meter
        dummy_container = abjad.Container(
            abjad.mutate(dummy_container[start : end]).copy()
        )
        abjad.mutate(dummy_container[:]).rewrite_meter(
            window_size,
            boundary_depth=self._boundary_depth,
            maximum_dot_count=self._maximum_dot_count,
            rewrite_tuplets=self._rewrite_tuplets,
        )
        abjad.attach(abjad.TimeSignature(window_size),
                     abjad.select(dummy_container).leaf(0),
                     )
        self._current_window = dummy_container[:]
        dummy_container[:] = []

    ### PUBLIC PROPERTIES ###

    @property
    def contents(self) -> abjad.Container:
        r'The ``abjad.Container`` to be sliced and looped.'
        return copy.deepcopy(self._contents)

    @contents.setter
    def contents(self,
                 contents: abjad.Container,
                 ):
        if not isinstance(contents, abjad.Container):
            raise TypeError("'contents' must be 'abjad.Container' or "
                            "child class")
        if not abjad.select(contents).leaves().are_contiguous_logical_voice():
            raise ValueError("'contents' must be contiguous logical voice")
        if isinstance(contents, abjad.Score):
            self._contents = copy.deepcopy(contents[0])
        elif isinstance(contents, abjad.Tuplet):
            self._contents = abjad.Container([copy.deepcopy(contents)])
        else:
            self._contents = copy.deepcopy(contents)
        self._contents_length = abjad.inspect(self._contents[:]).duration()
        self._contents_no_time_signature = copy.deepcopy(self._contents)
        self._remove_all_time_signatures(self._contents_no_time_signature)
        self._is_first_window = True

    @property
    def head_position(self) -> abjad.Duration:
        r'The position of the head at the start of a looping window.'
        return self._head_position

    @head_position.setter
    def head_position(self,
                      head_position: Union[tuple, abjad.Duration],
                      ):
        r"""This setter method replaces the parent's one since the parent's
        method uses integers as input intead of tuples or ``abjad.Duration``.
        """
        if not isinstance(head_position,
                          (int, float, tuple, str, abjad.Duration),
                          ):
            raise TypeError("'head_position' must be a number, 'tuple', or "
                            "'abjad.Duration'")
        if abjad.Duration(head_position) >= self._contents_length:
            raise ValueError("'head_position' must be smaller than the "
                             "length of 'contents'")
        self._is_first_window = True
        self._head_position = abjad.Duration(head_position)

    @property
    def window_size(self) -> abjad.Meter:
        r'The length of the looping window.'
        return self._window_size

    @window_size.setter
    def window_size(self,
                    window_size: Union[int, float, tuple, abjad.Meter],
                    ):
        r"""This setter method replaces the parent's one since the parent's
        method uses integers as input intead of tuples or ``abjad.Duration``.
        """
        if not isinstance(window_size,
                          (int, float, tuple, str, abjad.Meter),
                          ):
            raise TypeError("'window_size' must be 'tuple' or 'abjad.Meter'")
        if (abjad.Meter(window_size).duration
                > self._contents_length - self._head_position):
            raise ValueError("'window_size' must be smaller than or equal "
                             "to the length of 'contents'")
        self._window_size = abjad.Meter(window_size)

    @property
    def step_size(self) -> abjad.Duration:
        r'The size of each step when moving the head.'
        return self._step_size

    @step_size.setter
    def step_size(self,
                  step_size: Union[tuple, abjad.Duration],
                  ):
        r"""This setter method replaces the parent's one since the parent's
        method uses integers as input intead of tuples or ``abjad.Duration``.
        """
        if not isinstance(step_size,
                          (int, float, tuple, str, abjad.Duration),
                          ):
            raise TypeError("'step_size' must be a 'tuple' or "
                            "'abjad.Duration'")
        self._step_size = abjad.Duration(step_size)

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
    def fill_with_rests(self) -> bool:
        r'When ``True``, the output will contain no time signatures.'
        return self._fill_with_rests

    @fill_with_rests.setter
    def fill_with_rests(self,
                        fill_with_rests: bool,
                        ):
        if not isinstance(fill_with_rests, bool):
            raise TypeError("'fill_with_rests' must be 'bool'")
        self._fill_with_rests = fill_with_rests

    @property
    def boundary_depth(self) -> Union[int, None]:
        r"Sets the argument ``boundary_depth`` of abjad's ``rewrite_meter()``."
        return self._boundary_depth

    @boundary_depth.setter
    def boundary_depth(self,
                       boundary_depth: Optional[int],
                       ):
        if boundary_depth is not None:
            if not isinstance(boundary_depth, int):
                raise TypeError("'boundary_depth' must be 'int'")
        self._boundary_depth = boundary_depth

    @property
    def maximum_dot_count(self) -> Union[int, None]:
        r"""Sets the argument ``maximum_dot_count`` of abjad's
        ``rewrite_meter()``.
        """
        return self._maximum_dot_count

    @maximum_dot_count.setter
    def maximum_dot_count(self,
                          maximum_dot_count: Optional[int],
                          ):
        if maximum_dot_count is not None:
            if not isinstance(maximum_dot_count, int):
                raise TypeError("'maximum_dot_count' must be 'int'")
        self._maximum_dot_count = maximum_dot_count

    @property
    def rewrite_tuplets(self) -> bool:
        r"""Sets the argument ``rewrite_tuplets`` of abjad's
        ``rewrite_meter()``.
        """
        return self._rewrite_tuplets

    @rewrite_tuplets.setter
    def rewrite_tuplets(self,
                        rewrite_tuplets: bool,
                        ):
        if not isinstance(rewrite_tuplets, bool):
            raise TypeError("'rewrite_tuplets' must be 'bool'")
        self._rewrite_tuplets = rewrite_tuplets

    ### PRIVATE PROPERTIES ###

    @property
    def _done(self) -> bool:
        r"""Boolean indicating whether the process is done (i.e. whether the
        head position has overtaken the ``contents`` length).

        This property replaces the parent's one since the parent's property
        uses the number of indeces of ``contents``.
        """
        if self._fill_with_rests:
            return (self._head_position >= self._contents_length
                    or self._head_position < 0)
        else:
            return (self._head_position >= self._contents_length
                    - self._head_position or self._head_position < 0)