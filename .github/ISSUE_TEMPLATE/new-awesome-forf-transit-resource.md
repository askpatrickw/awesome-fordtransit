---
name: New Awesome Ford Transit Resource
about: This Template has all the information you need to provide for a link to be
  added to the Aweomse Ford Transit List.
title: ''
labels: ''
assignees: 'askpatrickw'
body:
  - type: markdown
    attributes:
      value: |
        Please provide the following information and we will review your suggested link.
  - type: input
    id: url
    attributes:
      label: URL
      description: |
        Provide a link to the Transit specific page, use the site's search if that makes the link more specific to Transits.
    validations:
      required: true
  - type: input
    id: description
    attributes:
      label: Description
      description: |
        Give a brief description of the type of awesome resources this site provides. A brief list is good if there's a lot of types of stuff.
    validations:
      required: true
  - type: dropdown
    id: category
    attributes:
      label: Category
      options:
        - Community
        - Dealers
        - Engine Mods
        - Exterior
        - Heating and AC
        - Interior
        - Maintenance
        - Plumbing
        - Suppliers
        - Suspension and Lifts
        - Van Automation
        - Van Builds
        - Van Builders
        - Wheels and Tires
    validations:
      required: true
