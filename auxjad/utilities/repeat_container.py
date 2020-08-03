import abjad

from .close_container import close_container
from .container_is_full import container_is_full
from .remove_repeated_time_signatures import remove_repeated_time_signatures
from .reposition_clefs import reposition_clefs as reposition_clefs_
from .reposition_dynamics import reposition_dynamics as reposition_dynamics_
from .reposition_slurs import reposition_slurs as reposition_slurs_


def repeat_container(container: abjad.Container,
                     n: int,
                     *,
                     omit_time_signatures: bool = False,
                     force_identical_time_signatures: bool = False,
                     reposition_clefs: bool = True,
                     reposition_dynamics: bool = True,
                     reposition_slurs: bool = True,
                     ) -> abjad.Container:
    r"""This function returns an |abjad.Container| with ``n`` repetitions of
    an input container (of type |abjad.Container| or child class).

    Basic usage:
        The required arguments are an |abjad.Container| (or child class) and
        and :obj:`int` for the number of repetitions.

        >>> container = abjad.Container(r"c'4 d'4 e'4")
        >>> output_container = auxjad.repeat_container(container, 3)
        >>> abjad.f(output_container)
        {
            %%% \time 3/4 %%%
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
        }

        .. figure:: ../_images/image-repeat_container-1.png

    .. note::

        Notice that the time signatures in the output are commented out with
        ``%%%``. This is because Abjad only applies time signatures to
        containers that belong to a |abjad.Staff|. The present function works
        with either |abjad.Container| and |abjad.Staff|.

        >>> container = abjad.Container(r"c'4 d'4 e'4")
        >>> output_container = auxjad.repeat_container(container, 3)
        >>> abjad.f(output_container)
        {
            %%% \time 3/4 %%%
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
        }

        .. figure:: ../_images/image-close_container-2.png

        >>> staff = abjad.Staff([output_container])
        >>> abjad.f(output_container)
        {
            \time 3/4
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
        }

        .. figure:: ../_images/image-close_container-3.png

    Time signature changes:
        It handle containers with multiple measures and different time
        signatures.

        >>> container = abjad.Container(r"\time 3/4 c'2. \time 2/4 r2 g'2")
        >>> output_container = auxjad.repeat_container(container, 3)
        >>> abjad.f(output_container)
        {
            %%% \time 3/4 %%%
            c'2.
            %%% \time 2/4 %%%
            r2
            g'2
            %%% \time 3/4 %%%
            c'2.
            %%% \time 2/4 %%%
            r2
            g'2
            %%% \time 3/4 %%%
            c'2.
            %%% \time 2/4 %%%
            r2
            g'2
        }

        .. figure:: ../_images/image-repeat_container-4.png

    Underfull containers:
        It automatically closes a container if necessary.

        >>> container = abjad.Container(r"\time 3/4 c'4 d'4 e'4 f'2")
        >>> output_container = auxjad.repeat_container(container, 2)
        >>> abjad.f(output_container)
        {
            %%% \time 3/4 %%%
            c'4
            d'4
            e'4
            %%% \time 2/4 %%%
            f'2
            %%% \time 3/4 %%%
            c'4
            d'4
            e'4
            %%% \time 2/4 %%%
            f'2
        }

        .. figure:: ../_images/image-repeat_container-5.png

    ``omit_time_signatures``:
        To omit all time signatures, set the keyword argument
        ``omit_time_signatures`` to ``True``.

        >>> container = abjad.Container(r"c'4 d'4 e'4")
        >>> output_container = auxjad.repeat_container(
        ...     container,
        ...     3,
        ...     omit_time_signatures=True,
        ... )
        >>> abjad.f(output_container)
        {
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
        }

        .. figure:: ../_images/image-repeat_container-6.png

    ``force_identical_time_signatures``:
        To force identical time signatures to be repeated at every repetition,
        set the keyword argument  ``force_identical_time_signatures`` to
        ``True``.

        >>> container = abjad.Container(r"\time 5/4 c'2. d'4 e'4")
        >>> output_container = auxjad.repeat_container(
        ...     container,
        ...     3,
        ...     force_identical_time_signatures=True,
        ... )
        >>> abjad.f(output_container)
        {
            %%% \time 5/4 %%%
            c'2.
            d'4
            e'4
            %%% \time 5/4 %%%
            c'2.
            d'4
            e'4
            %%% \time 5/4 %%%
            c'2.
            d'4
            e'4
        }

        .. figure:: ../_images/image-repeat_container-7.png

    Input types:
        The input container can be of child classes such as |abjad.Staff|,
        and the output will be of the same type.

        >>> container = abjad.Staff(r"c'4 d'4 e'4")
        >>> output_staff = auxjad.repeat_container(container, 3)
        >>> abjad.f(output_staff)
        \new Staff
        {
            \time 3/4
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
            c'4
            d'4
            e'4
        }

        .. figure:: ../_images/image-repeat_container-8.png

    ``reposition_clefs``, ``reposition_dynamics``, and ``reposition_slurs``:
        By default, this function will automatically remove repeated clefs as
        well as handle slurs and dynamics.

        >>> container = abjad.Staff(r"\clef bass f4\pp( e4) d4(")
        >>> output_staff = auxjad.repeat_container(container, 3)
        >>> abjad.f(output_staff)
        \new Staff
        {
            \time 3/4
            \clef "bass"
            f4
            \pp
            (
            e4
            )
            d4
            (
            f4
            (
            e4
            )
            d4
            (
            f4
            (
            e4
            )
            d4
        }

        .. figure:: ../_images/image-repeat_container-9.png

        Set the optional keyword arguments ``reposition_clefs``,
        ``reposition_dynamics``, and ``reposition_slurs`` to ``False`` to
        disable these behaviours. Do note that LilyPond automatically ignore
        repeated indentical clefs as well as repeated slur starts when another
        slur is already active, but these will still be present in the score's
        source code.

        >>> container = abjad.Staff(r"\clef bass f4\pp( e4) d4(")
        >>> output_staff = auxjad.repeat_container(container,
        ...                                        3,
        ...                                        reposition_clefs=False,
        ...                                        reposition_dynamics=False,
        ...                                        reposition_slurs=False,
        ...                                        )
        >>> abjad.f(output_staff)
        \new Staff
        {
            \time 3/4
            \clef "bass"
            f4
            \pp
            (
            e4
            )
            d4
            (
            \clef "bass"
            f4
            \pp
            (
            e4
            )
            d4
            (
            \clef "bass"
            f4
            \pp
            (
            e4
            )
            d4
            (
        }

        .. figure:: ../_images/image-repeat_container-10.png

    ..  error::

        If a container is malformed, i.e. it has an underfilled measure before
        a time signature change, the function raises a :exc:`ValueError`
        exception.

        >>> container = abjad.Container(r"\time 5/4 g''1 \time 4/4 f'4")
        >>> output_container = auxjad.repeat_container(container)
        ValueError: 'container' is malformed, with an underfull measure
        preceding a time signature change
    """
    if not isinstance(container, abjad.Container):
        raise TypeError("first positional argument must be 'abjad.Container' "
                        "or child class")
    if not isinstance(n, int):
        raise TypeError("second positional argument must be 'int'")
    if not isinstance(omit_time_signatures, bool):
        raise TypeError("'omit_time_signatures' must be 'bool'")
    if not isinstance(force_identical_time_signatures, bool):
        raise TypeError("'force_identical_time_signatures' must be 'bool'")

    container_ = abjad.mutate(container).copy()
    if not container_is_full(container_):
        close_container(container_)
    output_container = abjad.mutate(container_).copy()
    for _ in range(n - 1):
        output_container.extend(abjad.mutate(container_).copy())
    if not force_identical_time_signatures:
        remove_repeated_time_signatures(output_container)
    if reposition_clefs:
        reposition_clefs_(output_container)
    if reposition_clefs:
        reposition_dynamics_(output_container)
    if reposition_clefs:
        reposition_slurs_(output_container)
    if omit_time_signatures:
        for leaf in abjad.select(output_container).leaves():
            if abjad.inspect(leaf).indicator(abjad.TimeSignature):
                abjad.detach(abjad.TimeSignature, leaf)
    return output_container
