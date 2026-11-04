# Attribution and scope

The MIT license covers the original project code and documentation. Third-party
code, fonts, media, data and model provenance retain their own terms. This is an
unofficial Instagram-style concept, with no affiliation with or endorsement by
Instagram or Meta. Instagram and other third-party names and marks belong to
their respective owners.

## Components

- PaddleOCR and PaddlePaddle: Apache-2.0. https://github.com/PaddlePaddle/PaddleOCR
- imagededup: Apache-2.0. https://github.com/idealo/imagededup
- Microsoft Presidio: MIT. https://github.com/data-privacy-stack/presidio
- Embla Carousel and emoji-picker-react: MIT; preserved notices are in
  `web/public/open-source-licenses.txt`.
- Flutter's archived client uses a font with its existing license at
  `mobile/assets/fonts/OFL.txt`. Keep that notice with the font.
- Photographic sources and licenses for the football-media expansion are in
  `web/public/photo-credits.html` and
  `web/public/media/football/attributions.json` where present. Those credits are
  not an exhaustive provenance audit of earlier stock media. Screenshots contain
  demonstration content; photographs do not imply endorsement or real account
  ownership. The project license does not relicense third-party media or marks.

## Models and datasets

`models/` contains independently trained JSON inference parameters, not upstream
notebooks, executable pickle files or raw training data. See `models/README.md`
and `ML_INTEGRATION.md` for sources, transformations and limitations.

The historical fake/spam dataset was read from the pinned upstream repository
Ajaysagayam/Detection_of_Fake_Accounts_in_Social_Media at commit
`f8dc984326eded77363e7466060cc7ee6d5d32b6`. The source audit found no license file
there. The likely original dataset is attributed to Bardiya Bakhshandeh,
*Instagram fake/spammer/genuine accounts* (March 2019), with CC BY 3.0 reported by
the secondary dataset documentation; mirrored transformations are not fully
documented. This repository does not redistribute those raw CSVs or assert that
all upstream material is MIT licensed. Review source terms before downloading,
redistributing or using the data for a different purpose.

The pair-model training set is generated from fictional profile pairs by this
project. Its performance on real account-copy cases has not been established.

Meta Muse Spark is accessed through the Meta Model API with the developer's own
server-side key and applicable provider terms; no Meta model weights are bundled.
