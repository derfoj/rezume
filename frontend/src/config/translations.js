
export const translations = {
    fr: {
        nav: {
            logout: "Déconnexion",
            settings: "Paramètres",
            login: "Se connecter",
            start: "Commencer"
        },
        avatars: {
            man_laptop: "le geek du coin",
            woman_laptop: "la bosseuse",
            man_coffee: "le gars chill",
            woman_rocket: "la rocket girl",
            marc_aurel: "Le Marc Aurel du coin (l'intello)",
            avatar_femme: "La joyeuse"
        },
        hero: {
            greeting: "Hey!,",
            subtitle: "Gérez votre carrière avec nos outils alimentés par l'IA.",
            edit_title_placeholder: "Modifier titre"
        },
        landing: {
            badge: "IA PARAMÉTRÉE POUR L'EMPLOI",
            title: "Votre CV, optimisé par",
            titleHighlight: "l'Intelligence Artificielle",
            subtitle: "Passez les filtres ATS et décrochez plus d'entretiens. reZume analyse les offres et adapte votre parcours instantanément.",
            ctaPrimary: "Optimiser mon CV maintenant !",
            ctaSecondary: "Voir la démo",
            features: {
                ats: { title: "Anti-ATS", desc: "Structure LaTeX optimisée pour être lue par les robots recruteurs." },
                tailored: { title: "Sur-mesure", desc: "L'IA pioche dans vos expériences et les réécrit pour coller parfaitement à chaque offre." },
                privacy: { title: "Données Privées", desc: "Vos données restent dans votre espace personnel sécurisé." }
            },
            footer: "Développé par NZ Systems"
        },
        cards: {
            editor: {
                title: "Modifier mon Profil",
                desc: "Mettez à jour vos expériences, compétences et formations. C'est la base de connaissances que l'IA utilisera.",
                action: "Accéder à l'éditeur"
            },
            builder: {
                title: "Générateur de CV",
                desc: "Analysez une offre d'emploi et laissez l'IA générer un CV sur-mesure pour maximiser vos chances.",
                action: "Lancer le générateur"
            },
            explore: {
                title: "Galerie de Designs",
                desc: "Choisissez parmi une sélection de modèles de CV professionnels (Classique, Moderne, Tech...).",
                action: "Explorer les styles"
            }
        },
        profile: {
            title: "Mon Profil",
            subtitle: "Gérez vos informations pour l'IA et vos CVs.",
            back: "Retour Dashboard",
            sections: {
                general: "Infos Générales",
                skills: "Compétences",
                languages: "Langues",
                experiences: "Expériences",
                education: "Formation"
            },
            fields: {
                fullName: "Nom complet",
                currentTitle: "Titre actuel",
                summary: "Résumé / Bio",
                summaryPlaceholder: "Courte description professionnelle...",
                portfolio: "Portfolio URL",
                linkedin: "LinkedIn URL",
                skillPlaceholder: "Ex: Python...",
                langName: "Langue",
                levels: {
                    beginner: "Débutant",
                    intermediate: "Intermédiaire",
                    advanced: "Avancé",
                    fluent: "Bilingue",
                    native: "Natif"
                }
            },
            actions: {
                save: "Enregistrer les modifications",
                saving: "Enregistrement...",
                add: "Ajouter",
                importCV: "Importer depuis un CV (PDF)",
                importing: "Analyse du CV en cours..."
            },
            empty: {
                experiences: "Aucune expérience.",
                education: "Aucune formation."
            }
        },
        forms: {
            exp: {
                title: "Titre du poste",
                company: "Entreprise",
                desc: "Description",
                descPlaceholder: "Décrivez vos tâches, réalisations et technologies utilisées...",
                start: "Date de début",
                end: "Date de fin",
                cancel: "Annuler",
                save: "Sauvegarder"
            },
            edu: {
                degree: "Diplôme / Grade",
                degreePlaceholder: "Ex: Master Informatique",
                school: "Établissement",
                schoolPlaceholder: "Ex: Université de Paris",
                mention: "Mention",
                mentionPlaceholder: "Ex: Bien, Très bien",
                desc: "Description (Optionnel)",
                descPlaceholder: "Détails sur les cours, projets...",
                start: "Date de début",
                end: "Date de fin",
                cancel: "Annuler",
                save: "Sauvegarder"
            }
        },
        builder: {
            header: "SYSTEM ONLINE",
            mode: "WHITE MODE",
            backendOnline: "BACKEND CONNECTED",
            backendOffline: "BACKEND OFFLINE",
            input: {
                label: "TARGET INPUT STREAM",
                placeholder: "Collez l'offre d'emploi ici...",
                testData: "Insert Test Data"
            },
            actions: {
                process: "Lancer la séquence de génération",
                processing: "Traitement en cours...",
                download: "Télécharger CV",
                generating: "Génération..."
            },
            stats: {
                database: "Database Stats",
                xpVectors: "XP Vectors",
                skills: "Skills"
            },
            results: {
                optimizationComplete: "OPTIMIZATION COMPLETE",
                summary: "MATCH SUMMARY",
                skillsDetected: "SKILLS DETECTED",
                experiencesMatched: "EXPÉRIENCES SÉLECTIONNÉES"
            },
            widget: {
                title: "Semantic Similarity",
                subtitle: "Vector distance analysis."
            }
        },
        modals: {
            avatar: {
                title: "Quel genre d'étudiant êtes-vous ?",
                subtitle: "Sélectionnez l'avatar qui vous correspond le mieux."
            },
            settings: {
                title: "Paramètres",
                subtitle: "Personnalisez votre expérience.",
                language: "Langue de l'interface",
                theme: "Thème",
                light: "Clair",
                dark: "Nuit",
                linkedin: "Profil LinkedIn",
                apiKey: "OpenAI API Key",
                optional: "(Optionnel)",
                aiSection: "Intelligence Artificielle",
                provider: "Fournisseur",
                model: "Modèle",
                modelHint: "Assurez-vous que le modèle correspond au fournisseur.",
                soon: "Plus d'options bientôt disponibles (Thème, Clé API...)"
            }
        },
        toasts: {
            avatar_success: "Avatar mis à jour avec succès !",
            avatar_error: "Echec de la mise à jour de l'avatar",
            title_success: "Titre mis à jour !",
            title_error: "Erreur lors de la mise à jour du titre",
            lang_success: "Langue changée en",
            lang_error: "Erreur lors du changement de langue",
            analysis_success: "Analyse terminée avec succès !",
            analysis_error: "Erreur lors de l'analyse :",
            pdf_success: "CV téléchargé avec succès.",
            pdf_error: "Échec de la génération du PDF."
        }
    },
    en: {
        nav: {
            logout: "Logout",
            settings: "Settings",
            login: "Login",
            start: "Get Started"
        },
        avatars: {
            man_laptop: "the neighborhood geek",
            woman_laptop: "the hard worker",
            man_coffee: "the chill guy",
            woman_rocket: "the rocket girl",
            marc_aurel: "The local Marcus Aurelius (the nerd)",
            avatar_femme: "The joyful one"
        },
        hero: {
            greeting: "Hey!,",
            subtitle: "Manage your career with our AI-powered tools.",
            edit_title_placeholder: "Edit title"
        },
        landing: {
            badge: "AI TUNED FOR EMPLOYMENT",
            title: "Your CV, optimized by",
            titleHighlight: "Artificial Intelligence",
            subtitle: "Pass ATS filters and land more interviews. reZume analyzes job offers and adapts your background instantly.",
            ctaPrimary: "Optimize my CV now!",
            ctaSecondary: "View Demo",
            features: {
                ats: { title: "ATS-Proof", desc: "LaTeX structure optimized to be read by recruiter bots." },
                tailored: { title: "Tailor-made", desc: "AI picks from your experiences and rewrites them to perfectly match each offer." },
                privacy: { title: "Private Data", desc: "Your data stays in your secure personal space." }
            },
            footer: "Developed by NZ Systems"
        },
        cards: {
            editor: {
                title: "Edit My Profile",
                desc: "Update your experiences, skills, and education. This is the knowledge base the AI will use.",
                action: "Go to Editor"
            },
            builder: {
                title: "CV Generator",
                desc: "Analyze a job offer and let AI generate a tailored CV to maximize your chances.",
                action: "Launch Generator"
            },
            explore: {
                title: "Design Gallery",
                desc: "Choose from a selection of professional CV templates (Classic, Modern, Tech...).",
                action: "Explore Styles"
            }
        },
        profile: {
            title: "My Profile",
            subtitle: "Manage your information for AI and CVs.",
            back: "Back to Dashboard",
            sections: {
                general: "General Info",
                skills: "Skills",
                languages: "Languages",
                experiences: "Experiences",
                education: "Education"
            },
            fields: {
                fullName: "Full Name",
                currentTitle: "Current Title",
                summary: "Summary / Bio",
                summaryPlaceholder: "Short professional description...",
                portfolio: "Portfolio URL",
                linkedin: "LinkedIn URL",
                skillPlaceholder: "Ex: Python...",
                langName: "Language",
                levels: {
                    beginner: "Beginner",
                    intermediate: "Intermediate",
                    advanced: "Advanced",
                    fluent: "Fluent",
                    native: "Native"
                }
            },
            actions: {
                save: "Save Changes",
                saving: "Saving...",
                add: "Add"
            },
            empty: {
                experiences: "No experiences added.",
                education: "No education added."
            }
        },
        forms: {
            exp: {
                title: "Job Title",
                company: "Company",
                desc: "Description",
                descPlaceholder: "Describe your tasks, achievements, and technologies used...",
                start: "Start Date",
                end: "End Date",
                cancel: "Cancel",
                save: "Save"
            },
            edu: {
                degree: "Degree / Grade",
                degreePlaceholder: "Ex: Master in CS",
                school: "Institution",
                schoolPlaceholder: "Ex: University of Paris",
                mention: "Mention",
                mentionPlaceholder: "Ex: Honors",
                desc: "Description (Optional)",
                descPlaceholder: "Details about courses, projects...",
                start: "Start Date",
                end: "End Date",
                cancel: "Cancel",
                save: "Save"
            }
        },
        builder: {
            header: "SYSTEM ONLINE",
            mode: "WHITE MODE",
            backendOnline: "BACKEND CONNECTED",
            backendOffline: "BACKEND OFFLINE",
            input: {
                label: "TARGET INPUT STREAM",
                placeholder: "Paste raw job offer here...",
                testData: "Insert Test Data"
            },
            actions: {
                process: "Initialize Generation Sequence",
                processing: "Processing...",
                download: "Download CV",
                generating: "Generating..."
            },
            stats: {
                database: "Database Stats",
                xpVectors: "XP Vectors",
                skills: "Skills"
            },
            results: {
                optimizationComplete: "OPTIMIZATION COMPLETE",
                summary: "MATCH SUMMARY",
                skillsDetected: "SKILLS DETECTED",
                experiencesMatched: "SELECTED EXPERIENCES"
            },
            widget: {
                title: "Semantic Similarity",
                subtitle: "Vector distance analysis."
            }
        },
        modals: {
            avatar: {
                title: "What kind of student are you?",
                subtitle: "Select the avatar that suits you best."
            },
            settings: {
                title: "Settings",
                subtitle: "Customize your experience.",
                language: "Interface Language",
                theme: "Theme",
                light: "Light",
                dark: "Dark",
                linkedin: "LinkedIn Profile",
                apiKey: "OpenAI API Key",
                optional: "(Optional)",
                aiSection: "Artificial Intelligence",
                provider: "Provider",
                model: "Model",
                modelHint: "Ensure the model matches the provider.",
                soon: "More options coming soon (Theme, API Key...)"
            }
        },
        toasts: {
            avatar_success: "Avatar updated successfully!",
            avatar_error: "Failed to update avatar",
            title_success: "Title updated!",
            title_error: "Error updating title",
            lang_success: "Language changed to",
            lang_error: "Error changing language",
            analysis_success: "Analysis complete!",
            analysis_error: "Analysis error:",
            pdf_success: "CV downloaded successfully.",
            pdf_error: "PDF Generation failed."
        }
    }
};
