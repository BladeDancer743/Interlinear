# Web annotation layout

This document defines layout behavior for the separately launched Interlinear
Web workbench. It is not part of the installable terminal Skill.

## Core rule

Keep source geometry intact. Anchor explanations to source text, but do not
force long notes into the author's line boxes. A readable annotation has two
separate layers:

1. a compact numbered highlight at the exact source location;
2. an explanation card placed where it does not cover source text.

Save annotations separately while editing. When exporting a PDF, create a new
file with standard highlight and comment annotations; never overwrite the
source file.

## Layout decision

Choose one mode per page. Re-evaluate after zoom, viewport, note count, or note
length changes.

| Mode | Choose when | Presentation |
|:--|:--|:--|
| `margin` | Side space is at least 300 CSS px; at most 10 notes; longest note is at most 260 characters; cards fit within 92% of page height | Show all cards beside the page and connect them to numbered anchors |
| `focus` | The page is readable but there is not enough room for every card | Show all numbered anchors and one active card outside the source page |
| `list` | Viewport is under 720 CSS px; page uses over 88% of viewport width; over 12 notes; or a note exceeds 420 characters | Show numbered anchors plus a page-level note list |

Treat thresholds as defaults, not universal typography constants. A user
selection of `margin`, `focus`, or `list` overrides automatic choice.

## Collision handling

For margin cards:

1. Sort cards by anchor vertical position.
2. Center each card on its anchor when possible.
3. Push later cards down to preserve at least 12 CSS px between cards.
4. If the last card crosses the page bottom, distribute overflow upward.
5. If all cards still do not fit, switch the page to `focus`.

Do not shrink body text below a comfortable reading size merely to keep margin
mode.

## Medium-specific behavior

- **Short chat passage**: retain `term【翻译：作用】` when it remains readable.
- **Long Markdown or reflowable text**: use light inline markers plus a glossary
  when density control omits useful terms.
- **PDF or fixed page**: use coordinate highlights and external cards; export
  standard PDF highlight/comment objects.
- **Mobile or narrow pane**: use a numbered list after the page or section.
- **Print**: include anchor numbers and a page-note appendix because popup
  comments are not visible on paper.

## Quality checks

- No explanation card covers source text, equations, citations, or figures.
- Anchor numbers remain stable across layout modes.
- Keyboard and pointer users can open the same note.
- Confidence markers remain visible in every mode.
- Manual layout choice is preserved until the user changes it.
- Exported PDF opens with annotations in a standard reader.
