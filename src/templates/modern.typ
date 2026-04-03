// --- Template modern.typ (Version Premium) ---

#let resume(
  name: "Jean Dupont",
  title: "Ingénieur Logiciel",
  email: "",
  phone: "",
  linkedin: "",
  portfolio: "",
  summary: "",
  photo_path: none,
  experiences: (),
  education: (),
  skills: (
    hard: "",
    soft: "",
  ),
  languages: "",
) = {
  // --- Configuration de la Page (Format LaTeX 0.5in margins) ---
  set page(
    paper: "a4",
    margin: (x: 1.27cm, y: 1.27cm),
  )
  
  // --- Styles de Texte ---
  // On utilise des polices standards professionnelles disponibles sur Windows/Linux
  set text(font: "Libertinus Serif", size: 10pt, fill: rgb("#000000"), lang: "fr")
  
  // Interligne serré mais lisible (LaTeX style)
  set par(leading: 0.55em, justify: true)
  
  let primary_color = rgb("#000000") // Noir pur pour le look classique LaTeX
  
  // --- Fonction pour les titres de section (Style \scshape \titlerule) ---
  let section(title) = {
    v(8pt, weak: true)
    block(width: 100%)[
      #text(11pt, weight: "bold")[#smallcaps(title)]
      #v(-8pt)
      #line(length: 100%, stroke: 0.6pt + primary_color)
    ]
    v(2pt)
  }

  // --- En-tête (Layout Minipage LaTeX) ---
  grid(
    columns: (1fr, 3fr),
    gutter: 15pt,
    if photo_path != none {
      // Image avec coins légèrement arrondis ou simple cadre
      block(stroke: 0.5pt + gray, inset: 0pt, radius: 2pt)[
        #image(photo_path, width: 3cm)
      ]
    } else {
      none
    },
    align(center + horizon)[
      #v(-10pt)
      #text(24pt, weight: "bold")[#smallcaps(name)] \
      #v(4pt)
      #text(11pt, weight: "bold")[#smallcaps(title)] \
      #v(6pt)
      #text(9pt)[
        #if portfolio != "" [🌐 #link(portfolio)[#underline[Portfolio]] #h(8pt)]
        #if linkedin != "" [ #link("https://" + linkedin)[#underline[LinkedIn]] #h(8pt)]
        #if email != "" [✉ #link("mailto:" + email)[#underline[#email]]]
      ]
    ]
  )

  v(5pt)

  // --- Formation ---
  if education.len() > 0 {
    section("Formation")
    for edu in education {
      grid(
        columns: (1fr, auto),
        [*#edu.institution*], [#text(style: "italic")[#edu.date]]
      )
      text(size: 9pt)[#edu.degree]
      v(2pt)
    }
  }

  // --- Expériences (Style \resumeSubheading) ---
  if experiences.len() > 0 {
    section("Expériences Professionnelles & Projets")
    for exp in experiences {
      block(width: 100%, breakable: false)[
        #grid(
          columns: (1fr, auto),
          [*#exp.company*], [#text(style: "italic")[#exp.date]]
        )
        #text(size: 9pt, weight: "semibold", style: "italic")[#exp.position] \
        #v(1pt)
        #if type(exp.description) == "array" {
          set list(indent: 12pt, marker: [•], spacing: 0.4em)
          for item in exp.description {
            list.item[#text(size: 9pt)[#item]]
          }
        } else {
          text(size: 9pt)[#exp.description]
        }
      ]
      v(4pt, weak: true)
    }
  }

  // --- Compétences ---
  section("Compétences Techniques")
  text(size: 9pt)[
    #skills.hard
  ]

  section("Compétences Personnelles")
  text(size: 9pt)[
    #skills.soft
  ]

  // --- Langues ---
  if languages != "" {
    section("Langues")
    text(size: 9pt)[#languages]
  }
}
