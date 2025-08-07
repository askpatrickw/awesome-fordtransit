---
name: New Awesome Ford Transit Resource
about: This Template has all the information you need to provide for a link to be
  added to the Awesome Ford Transit List.
title: ''
labels: 'new-resource'
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
  - type: checkboxes
    id: use_ai
    attributes:
      label: AI Generation
      description: Would you like AI to automatically generate the description and category?
      options:
        - label: Use AI to generate description and category
          required: false
  - type: input
    id: description
    attributes:
      label: Description (Optional if using AI)
      description: |
        Give a brief description of the type of awesome resources this site provides. A brief list is good if there's a lot of types of stuff.
        Leave blank if you selected AI generation above.
    validations:
      required: false
  - type: dropdown
    id: category
    attributes:
      label: Category (Optional if using AI)
      description: |
        Select the category for this resource. Leave blank if you selected AI generation above.
      options:
        - ""
        - Community
        - Dealers
        - Engine Mods
        - Exterior
        - Exterior - Bumpers
        - Exterior - Front Hooks
        - Exterior - Rear Shock Relocation
        - Exterior - Skid Plates
        - Exterior - Ski Boxes
        - Heating and AC
        - Interior
        - Maintenance
        - Plumbing
        - Suppliers
        - Suspension and Lifts
        - Seat Swivels
        - Van Automation
        - Van Builds
        - Van Builders
        - Wheels and Tires
    validations:
      required: false
  - type: textarea
    id: override_suggestion
    attributes:
      label: Override AI Suggestion (Optional)
      description: |
        If you're using AI generation but want to suggest a different category or description, provide it here.
      placeholder: "e.g., I think this should go in 'Exterior - Bumpers' instead"
    validations:
      required: false
