# Dossier Concept Simulator 1.0.0

Interactive WordPress simulator for the 19-record S24 concept-mapping example: 12 concepts, nine relationships and 33 reviewed excerpts.

## Installation

1. In WordPress, open Plugins > Add New Plugin > Upload Plugin.
2. Upload `dossier-concept-simulator-v1.0.0.zip`, install it, and activate **Dossier Concept Simulator**.
3. Open **Tools > Concept Simulator** while signed in as an administrator.
4. To show it within a page, add a Shortcode block containing `[dossier_concept_simulator]`. A full-width page template gives the map more room.

The Tools page and shortcode are administrator-only (`manage_options`). Other visitors receive an access notice without the excerpt dataset. Activation does not create pages, modify records or publish the map. No settings or database tables are added.

## Exploring the simulator

- **Map:** click a concept card for definitions and support. Click a relationship number or use the relationship list to see the typed link and its interpretation limit.
- **Evidence:** inspect the currently visible excerpts, statement types and source locators.
- **Sample simulator:** switch to the original four records, restore all 19, or include/exclude records individually. Selected records may still be hidden by the mailbox filter.
- **Find a concept:** matches concept labels and definitions, not full email contents.
- **Mailbox:** restrict support to Bailey, Rapp or Pereira.
- **Records per concept:** require more distinct sampled records before a concept appears.
- **Hide forecast / possibility excerpts:** removes excerpts explicitly typed as forecasts or possibilities; other types, including questions and uncertainty, remain visible.
- **Restore all:** resets the sample and filters. Browser refresh also resets them.

Counts represent distinct sampled records, not people or events. A relationship remains visible only if both concepts are visible and every cited excerpt remains available. The baseline map is fixed, not an AI model performing new extraction. Filtering is an exploratory what-if operation; it does not revise the formal findings or establish causation.

At narrow screen widths the graph scrolls horizontally and the detail panel moves below it. Concepts and relationships support keyboard Enter/Space; tabs support arrow keys, Home and End. Multiple shortcode instances have independent state.

## Dataset and boundaries

Source: Dossier Space session DS-20260905-S24, four inherited plus 15 additional email records. Mailboxes: Bailey (9), Rapp (5), Pereira (5). This is a convenience example, not an exhaustive taxonomy or representative corpus sample. Quoted chains are not independent corroboration. Assertions, requests, denials and predictions retain their interpretation limits.

Only the 33 reviewed excerpts, concepts, relationships and source identifiers are bundled. Full message bodies, attachments, local drive paths, credentials and source archives are not included. Data is held in an ABSPATH-guarded PHP include; assets contain interface code only. No remote libraries, analytics, API calls or external network requests are used. No uploads, writes to the corpus, automatic updates to the data, or persistent simulation settings are implemented.

## Validation

Browser interaction tests passed in headless Microsoft Edge: initial counts, baseline four, empty sample, evidence loss after exclusions, mailbox/threshold/search filters, forecast filter, source locators, keyboard controls, 390px page layout, two independent instances, unique IDs, no script errors and no network requests. Desktop layout visually inspected. Package and source-data integrity checks passed.

**Not yet tested in a running WordPress installation.** No PHP runtime was available locally for PHP lint or execution; the PHP entry point was reviewed and follows the WordPress shortcode/enqueue APIs. Declared compatibility: WordPress 6.0+, PHP 7.4+. Confirm activation and rendering on the intended WordPress installation before relying on it in a shared environment.

## Files

- `dossier-concept-simulator.php`: WordPress hooks, access checks and rendering.
- `assets/simulator.js` and `assets/simulator.css`: self-contained interface.
- `includes/data.php`: fixed source-derived excerpt dataset.

The separate `concept-simulator-preview.html` runs offline by opening it in a browser; it contains the same excerpt dataset and UI, without WordPress access control. It is a preview file, not a plugin upload.

## Source and licence

Plugin code: GPL-2.0-or-later. EDRM source material remains under its stated licence: Creative Commons Attribution 3.0 United States. Attribution: ZL Technologies, Inc. (http://www.zlti.com). No endorsement is implied.

WordPress implementation references: https://developer.wordpress.org/reference/functions/add_shortcode/ and https://developer.wordpress.org/reference/functions/wp_enqueue_script/ .
