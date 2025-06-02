![](media/image1.png){width="1.0520833333333333in"
height="1.0416666666666667in"}![](media/image2.png){width="2.6185192475940506in"
height="1.0589599737532809in"}

**Handover Plan**

Museum of Vertebrate Zoology

Karishma Mehta, Somdeb Mukhopadhyay, Shivani Tayade, Ji Yeon Woo

This handover plan outlines the following: specific deliverables to be
handed over from the UC Davis MSBA Practicum team to the Museum of
Vertebrate Zoology / Arctos Consortium, the form each deliverable will
be provided in, a timeline for each deliverable, the intended recipient
of each deliverable, and the intended impact of the deliverable.

### Specifics of Final Deliverables and Processes

Based on discussions with the MIP and the Statement of Work, there are 4
major deliverables the team will hand over. Below is a list of the
deliverables with an explanation of each deliverable.

1.  **Tableau Dashboard**: A dynamic, user-friendly dashboard
    summarizing key Arctos usage metrics (e.g., institution
    contributions, number of records, taxon records, counts of research
    and media). The dashboard consists of a bar chart that displays the
    number of records from each institution, a pie chart that displays
    the percentage of contributions from each institution, and bar
    charts displaying system statistics. The dashboard also includes
    spatial analysis in the form of an interactive map that shows record
    count, record type, and year collected.

2.  **AI-Powered Chatbot**: Two different assistive chatbots were
    developed to help Arctos users generate search queries from natural
    language. The first chatbot is a custom GPT-based assistant
    prototype built using OpenAI ChatGPT platform and integrated with
    Arctos documentation to help users construct Arctos search query
    URLs. It is prompt-based, lightweight, and easy to update with new
    documentation or improved prompting strategies. The second, and the
    primary chatbot is a Streamlit web application that connects the
    OpenAI API (GPT-3.5) with the Arctos database API. It parses natural
    language queries into structured parameters (e.g., taxon, locality,
    year), maps them to Arctos search fields, and generates valid Arctos
    search URLs. It uses rule-based parsing for query interpretation,
    singularization of common names, special field handling (e.g.,
    is_tissue, part_search), and conditional logic for taxonomy
    mapping.Additionally, the Streamlit chatbot includes Google Sheets
    logging functionality: every search query, along with its extracted
    fields and generated URL, is automatically logged with a timestamp
    in a shared Google Sheet. This provides a transparent, structured
    record of usage for future analysis, monitoring, or refinement of
    the chatbot's performance. The app is publicly deployed on Streamlit
    Community Cloud and open-sourced via GitHub, with all logic, UI
    code, and deployment configuration documented for ease of
    maintenance.

3.  **Documentation**: As the above deliverables require transfer of
    knowledge, a step-by-step user guide for the dashboard and chatbot
    will be important to ensure no knowledge is lost and managing these
    tools can continue beyond this Practicum's span. This document will
    outline how to utilize the dashboard and chatbot as well as
    instructions on how to deploy it and update it, serving as technical
    documentation for maintenance and future improvements by the Arctos
    team.

4.  **Handover Workshop / Training Session**: Our team will walk through
    the steps to update the dashboard and chatbot over Zoom, showing
    Arctos staff and programmers how to use the dashboard and chatbot
    effectively. This final training session will capture final feedback
    and answer any remaining questions.

### Delivery Method of Deliverables

1.  **Tableau Dashboard**: The finalized Tableau dashboard will be
    delivered in two formats. It will first be delivered as an
    interactive Tableau Public link on team member Shivani Tayade's
    account, where it is currently hosted. This allows for immediate use
    and interaction, as the Tableau dashboard is currently available on
    the Arctos website. The file containing the Dashboard will also be
    transferred to a Tableau public account managed by Arctos.

> The second format is a packaged workbook file shared via Google Drive
> for backup and archival purposes. A fully packaged Tableau workbook
> file will be transferred to the Arctos team to enable future
> customizations, updates, and rehosting on the institution's own
> Tableau server or online workspace as desired.

2.  **AI-Powered Chatbot**: The two chatbot prototypes will be delivered
    in modular, editable formats. The GPT-based chatbot does not consist
    of code, but is hosted on OpenAI's ChatGPT as a custom GPT. The
    instructions given to the custom GPT will be retrieved and shared to
    the Arctos team as a written document and shared via GitHub. As the
    custom GPT cannot be handed over to another ChatGPT account, the
    guidelines used to build the custom GPT will have to be fed to
    another custom GPT made by and maintained by the Arctos team.

> The second chatbot is a fully functional, open-source Streamlit web
> app that accepts natural language queries and dynamically extracts key
> fields (e.g., taxon, location, date). It then uses a rule-based
> mapping layer to generate valid Arctos search URLs by calling the
> Arctos API and integrates responses from the OpenAI API (GPT-3.5). The
> app has a front-end interface, and backend code includes logic for
> query interpretation, singularization of common names, field mapping,
> and URL generation. API keys are managed securely using Streamlit's
> secrets.toml. The entire solution is modular, editable, and deployed
> via Streamlit Community Cloud for easy public access, with the GitHub
> repository serving as the single source of deployment and
> documentation. In addition, the app logs each user query, extracts
> parameters, and generates a URL to a connected Google Sheet in real
> time using a Google Cloud service account. This provides a transparent
> record of usage activity and supports future analysis and monitoring.

3.  **Documentation**: Documentation will be shared in the project
    team's GitHub repository and includes the following:

    a.  User Guide (PDF): A step-by-step manual on how to use the
        Tableau dashboard and the chatbots.

    b.  Technical Manual: Includes setup and chatbot deployment
        instructions, guidelines for editing prompts or system messages,
        connecting to updated Arctos documentation, and how to republish
        the dashboard if data is updated.

4.  **Handover Workshop / Training Session**: The handover session will
    be conducted over Zoom. It will include live walkthroughs of the
    dashboard and chatbot, demonstration of how to update the data for
    the dashboard, and demonstrations of how to update the chatbots. The
    session will also include a Q&A session to answer any final
    stakeholder or end-user questions. If requested, a follow-up office
    hour can be arranged.

### Deliverable Timeline and Dependencies

|                                                           |                  |                                                                                                                                                                                             |
|-----------------------------------------------------------|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Task**                                                  | **Planned Date** | **Dependencies & Notes**                                                                                                                                                                    |
| *Finalize Tableau Dashboard*                              | Completed        | Incorporate final data updates and verify accuracy of spatial analysis.                                                                                                                     |
| *Transfer Tableau Workbook File*                          | April 30         | Requires confirmation of preferred storage destination (e.g., Google Drive or GitHub repository). Also requires ensuring that there is enough storage space for the selected method.        |
| *Document GPT Instructions for Custom Chatbot*            | May 13           | Retrieve current prompt structure and settings from ChatGPT; validate with Arctos team that format is reproducible.                                                                         |
| *Publish Streamlit Chatbot App & Documentation to GitHub* | May 15           | Ensures the Streamlit app is functional, OpenAI and Arctos API keys are secured, and the GitHub repo includes the full codebase, documentation, and deployment instructions for Arctos use. |
| *Finalize Documentation (User Guide + Technical Manual)*  | May 20           | Relies on final versions of dashboard and both chatbots to ensure complete and accurate instructions.                                                                                       |
| *Prepare for Handover Workshop*                           | May 24           | Includes scheduling a Zoom session with Arctos team, preparing slides, test-running the demos, and gathering final questions.                                                               |
| *Handover Workshop & Training Session*                    | June 1           | Live walkthroughs of the dashboard and both chatbots. Attendance from Arctos staff and stakeholders desired.                                                                                |
| *Optional: Office Hours or Follow-Up Support*             | Upon request     | Arranged based on feedback from the handover workshop.                                                                                                                                      |

### Intended Recipients

1.  **Tableau Dashboard**: Arctos team, particularly the developers and
    Arctos leadership such as Michelle Koo, the MIP. The dashboard can
    also be extended to be available to curators or researchers who are
    interested in exploring the dashboard and editing it to fit their
    own needs, if allowed by the Arctos team.

2.  **AI-Powered Chatbot**: Arctos programming team. The deliverables
    will be transferred to the programming team to ensure they can be
    replicated or used with accounts managed by the Arctos team.

3.  **Documentation**: Arctos team, particularly developers and
    programmers, staff, and leadership. Some parts of the documentation
    such as the user guide will also be intended for curators and
    researchers that use data from the Arctos Consortium. Other parts of
    the documentation such as the technical guide will be directed
    primarily to the Arctos team so they can continue to update the
    deliverables as needed.

4.  **Handover Workshop / Training Session**: Arctos team, particular
    developers, programmers, and leadership. The training session and
    handover workshop will also be helpful for the MSBA team, as it will
    help our team clear up any questions that the Arctos team may have
    regarding the deliverables and the documentation. Attendees will
    primarily be from the main Arctos team, such as MIP Michelle Koo and
    programmers recommended by Michelle.

### Intended Impact and Effect

Together, the deliverables below represent a meaningful and sustainable
enhancement to the Arctos user experience. The Tableau dashboard offers
immediate insights for decision-makers, the AI-powered chatbots lower
barriers to access for a diverse user base, and the comprehensive
documentation and training ensure that the tools are maintainable and
scalable over time. The success of the practicum will ultimately be
measured by the extent to which these solutions are adopted, integrated
into existing workflows, and continue to empower the Arctos team and
broader research community long after the project concludes. By
delivering tools that are functional, user-centered, and future-proofed,
this engagement sets the foundation for lasting impact.

1.  **Tableau Dashboard**: Enhances visibility into Arctos system usage
    and institutional contributions, supporting data-driven
    decision-making for both internal management and external reporting.
    By providing an intuitive visual summary of complex records data, it
    improves stakeholder engagement and empowers curators and
    researchers to identify patterns and opportunities for curation,
    outreach, and data entry improvements. The dashboard's long-term
    value lies in its adaptability and its potential integration into
    Arctos\'s core infrastructure.

2.  **AI-Powered Chatbot**: Significantly reduces the cognitive and time
    burden associated with constructing Arctos queries, especially for
    non-technical users. The GPT-based chatbot improves accessibility by
    allowing natural language interaction, while the code-based chatbot
    provides a customizable, scalable foundation for future development.
    Together, they demonstrate the feasibility of assistive tools that
    can evolve alongside Arctos documentation and user needs.

3.  **Documentation**: Ensures long-term sustainability and independence
    of Arctos staff in managing and evolving the tools. Clear
    documentation facilitates smoother onboarding, reduces reliance on
    the original project team, and promotes tool adoption across
    technical and non-technical user groups. It also demonstrates best
    practices for reproducibility and institutional knowledge transfer.

4.  **Search Logging & Future Insights:** The integrated logging of
    search queries into Google Sheets creates a lightweight, live
    dataset of real-world usage. This record not only supports
    transparency and monitoring but can also serve as a valuable
    resource for future research into user behavior. Over time, patterns
    in query types, taxon frequencies, institutions of interest, and
    common geographic filters can be analyzed to understand researcher
    needs and inform improvements to both the chatbot and the Arctos
    platform itself. This lays the groundwork for data-driven feature
    prioritization, trend analysis, and broader usability research.

5.  **Handover Workshop / Training Session**: Builds capacity within the
    Arctos team to confidently use, maintain, and enhance the
    deliverables beyond the practicum. The session strengthens the
    relationship between the practicum team and MVZ / Arctos
    stakeholders, reinforces trust in the tools provided, and ensures a
    smooth transition. The feedback gathered during the session also
    serves as a final validation of the project\'s usability and value.
