import collections
from typing import Iterable, Union

import abjad


def leaves_are_tieable(leaves: Union[abjad.Selection,
                                     Iterable[Union[abjad.Component,
                                                    abjad.LogicalTie,
                                                    ]],
                                     ],
                       ) -> bool:
    r"""Returns a :obj:`bool` representing whether or not two input leaves (of
    type |abjad.Leaf| or child class) have identical pitch(es) and thus can
    be tied.

    Basic usage:
        When the pitches in both leaves are identical, this function returns
        ``True``:

        >>> leaf1 = abjad.Note(r"c'4")
        >>> leaf2 = abjad.Note(r"c'4")
        >>> auxjad.leaves_are_tieable(leaf1, leaf2)
        True

    Durations:
        Durations do not affect the comparison.

        >>> leaf1 = abjad.Note(r"c'2.")
        >>> leaf2 = abjad.Note(r"c'16")
        >>> leaf3 = abjad.Note(r"f'''16")
        >>> auxjad.leaves_are_tieable(leaf1, leaf2)
        Trueselection2
        >>> auxjad.leaves_are_tieable(leaf1, leaf3)
        False
        >>> auxjad.leaves_are_tieable(leaf2, leaf3)
        False

    Chords:
        Handles chords as well as pitches.

        >>> chord1 = abjad.Chord(r"<c' e' g'>4")
        >>> chord2 = abjad.Chord(r"<c' e' g'>16")
        >>> chord3 = abjad.Chord(r"<f''' fs'''>16")
        >>> auxjad.leaves_are_tieable(chord1, chord2)
        True
        >>> auxjad.leaves_are_tieable(chord1, chord3)
        False
        >>> auxjad.leaves_are_tieable(chord2, chord3)
        False

    Parentage:
        Leaves can also be part of containers.

        >>> container = abjad.Container(r"r4 <c' e'>4 <c' e'>2")
        >>> auxjad.leaves_are_tieable(container[1], container[2])
        True

    Rests:
        If rests are input, the return value is ``False``.

        >>> container = abjad.Container(r"r4 g'4 r2")
        >>> auxjad.leaves_are_tieable(container[0], container[2])
        False
    """
    if not isinstance(leaves, (abjad.Selection,
                               collections.abc.Iterable,
                               )):
        raise TypeError("argument must be 'abjad.Selection' or non-string "
                        "iterable of components")
    for index, leaf1 in enumerate(leaves[:-1]):
        for leaf2 in leaves[index + 1:]:
            if isinstance(leaf1, abjad.LogicalTie):
                leaf1 = leaf1[0]
            if isinstance(leaf2, abjad.LogicalTie):
                leaf2 = leaf2[0]
            if not isinstance(leaf1, type(leaf2)):
                return False
            if isinstance(leaf1, abjad.Rest):
                return False
            if isinstance(leaf1, abjad.MultimeasureRest):
                return False
            if (isinstance(leaf1, abjad.Note)
                    and leaf1.written_pitch != leaf2.written_pitch):
                return False
            if (isinstance(leaf1, abjad.Chord)
                    and leaf1.written_pitches != leaf2.written_pitches):
                return False
            leaf1_graces = abjad.inspect(leaf1).before_grace_container()
            leaf2_graces = abjad.inspect(leaf2).before_grace_container()
            if not isinstance(leaf1_graces, type(leaf2_graces)):
                return False
    return True


def _leaves_are_tieable(self):
    return leaves_are_tieable(self._client)


abjad.Inspection.leaves_are_tieable = _leaves_are_tieable
