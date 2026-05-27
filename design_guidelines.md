{
  "meta": {
    "project": "TAMIS AGRO — mobile adaptive modals + profile",
    "audience": "Farmers on smartphones (UA)",
    "breakpoint_mobile": "@media (max-width: 768px)",
    "non_goals": ["Do not change Navbar1/Header and Footer1"],
    "critical_constraints": [
      "Side padding on mobile: 20px",
      "Tap targets >= 44px",
      "No transition: all",
      "Avoid horizontal overflow",
      "iOS inputs must be >= 16px font-size (prevent zoom)",
      "Sticky bottom CTA must include env(safe-area-inset-bottom)",
      "All interactive + key informational elements must include data-testid"
    ]
  },

  "brand": {
    "attributes": ["trustworthy", "earthy", "calm", "practical", "high-contrast", "non-flashy"],
    "palette": {
      "cream": "#f9f7f2",
      "surface": "#ffffff",
      "dark_green": "#1b4332",
      "olive": "#aebb50",
      "neutral_grey": "#93928c",
      "danger": "#c0392b",
      "warning": "#e6b32a",
      "success": "#2d8659",
      "overlay": "rgba(15, 26, 20, 0.55)",
      "border": "#e7ebe7"
    },
    "typography": {
      "display": {
        "family": "Commissioner",
        "usage": ["modal titles", "section headings", "profile page title"]
      },
      "body": {
        "family": "Golos Text",
        "usage": ["forms", "tables/cards", "helper text"]
      },
      "scale": {
        "h1": "text-4xl sm:text-5xl lg:text-6xl",
        "h2": "text-base md:text-lg",
        "body": "text-base (mobile: text-sm)",
        "small": "text-sm or text-xs",
        "mobile_input_min": "16px"
      }
    },
    "radius_shadow": {
      "radius_sheet": "16px (top corners on mobile sheets)",
      "radius_card": "12px",
      "radius_control": "10px",
      "shadow_sheet": "0 -8px 32px rgba(15,26,20,.18)",
      "shadow_modal": "0 28px 60px rgba(15,26,20,.32)"
    }
  },

  "design_tokens_css": {
    "where": ["/app/frontend/src/index.css (preferred)", "or per-module :root in CSS modules if needed"],
    "tokens": ":root {\n  --agro-cream: #f9f7f2;\n  --agro-surface: #ffffff;\n  --agro-green: #1b4332;\n  --agro-olive: #aebb50;\n  --agro-grey: #93928c;\n  --agro-border: #e7ebe7;\n  --agro-overlay: rgba(15, 26, 20, 0.55);\n\n  --agro-danger: #c0392b;\n  --agro-warning: #e6b32a;\n  --agro-success: #2d8659;\n\n  --sheet-side: 20px;\n  --sheet-top: 16px;\n  --sheet-bottom: 24px;\n  --sheet-radius: 16px;\n\n  --tap: 44px;\n\n  --ease-sheet: cubic-bezier(0.2, 0.8, 0.2, 1);\n  --dur-sheet: 240ms;\n\n  --focus-ring: 0 0 0 3px rgba(174, 187, 80, 0.35);\n  --focus-outline: 2px solid #aebb50;\n}\n\n@media (prefers-reduced-motion: reduce) {\n  :root { --dur-sheet: 1ms; }\n}\n"
  },

  "universal_mobile_sheet_blueprint": {
    "goal": "Unify all mobile modal/drawer experiences into a native-feeling full-screen sheet with sticky footer CTA.",
    "structure": {
      "backdrop": {
        "position": "fixed inset:0",
        "background": "var(--agro-overlay)",
        "layout": "align-items: stretch; justify-content: stretch",
        "scroll": "backdrop should not scroll; sheet handles internal scroll",
        "z_index": ">= 9999"
      },
      "sheet": {
        "position": "relative (inside backdrop)",
        "size": "width: 100vw; height: 100vh; max-height: 100vh",
        "surface": "background: var(--agro-cream) or var(--agro-surface) depending on content density",
        "radius": "border-radius: 0 on full-screen; OR top corners 16px if using bottom-sheet variant",
        "layout": "display:flex; flex-direction:column; overflow:hidden",
        "animation": "transform translateY(12px)->0 + opacity 0->1; duration var(--dur-sheet) easing var(--ease-sheet)"
      },
      "sheet_header": {
        "height": "min 56px",
        "padding": "16px var(--sheet-side)",
        "layout": "display:flex; align-items:center; justify-content:space-between; gap:12px",
        "title": "Commissioner 18–20px, 600, color var(--agro-green)",
        "close": "Icon button >=44x44, top-right, focus-visible ring"
      },
      "sheet_body": {
        "padding": "0 var(--sheet-side) var(--sheet-bottom)",
        "scroll": "overflow-y:auto; -webkit-overflow-scrolling: touch",
        "safe_area": "body bottom padding should not include safe-area; footer handles it",
        "avoid_overflow": "min-width:0 on flex children; max-width:100% on images"
      },
      "sheet_footer_sticky": {
        "position": "sticky; bottom: 0",
        "padding": "12px var(--sheet-side) calc(12px + env(safe-area-inset-bottom))",
        "background": "var(--agro-cream) or var(--agro-surface)",
        "border_top": "1px solid rgba(44,44,39,0.10)",
        "cta": "Primary button full-width, height >=44px; secondary stacked or 2-col grid"
      }
    },
    "body_scroll_lock": {
      "js_guideline": {
        "when_open": "document.documentElement.style.overflow = 'hidden'; document.body.style.overflow = 'hidden';",
        "when_close": "restore previous overflow values",
        "ios_note": "Prefer locking html+body; avoid position:fixed hacks unless necessary"
      }
    },
    "micro_interactions": {
      "press": "button:active { transform: translateY(1px); } (only on buttons)",
      "hover": "background-color shift only; no transform on containers",
      "focus": "use :focus-visible outline or box-shadow ring; never remove outline without replacement",
      "transition_rule": "Only transition background-color, border-color, box-shadow, opacity (never all)"
    },
    "iconography": {
      "format": "inline SVG",
      "size_mobile": "20–24px",
      "stroke": "1.6–2",
      "color": "var(--agro-green) for primary actions; var(--agro-grey) for secondary"
    }
  },

  "file_specific_mobile_css": {
    "AuthModal.module.css": {
      "intent": "Centered desktop modal -> full-screen sheet on mobile with sticky submit.",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .backdrop {\n    padding: 0;\n    align-items: stretch;\n    justify-content: stretch;\n  }\n  .modal {\n    width: 100vw;\n    height: 100vh;\n    max-width: none;\n    max-height: none;\n    border-radius: 0;\n    padding: 16px 20px 0;\n    overflow: hidden;\n    display: flex;\n    flex-direction: column;\n    animation: sheetIn var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n  }\n  .header {\n    margin-bottom: 12px;\n    padding-right: 44px;\n  }\n  .title { font-size: 20px; }\n  .subtitle { font-size: 13px; }\n  .close {\n    top: 10px;\n    right: 10px;\n    width: 44px;\n    height: 44px;\n  }\n  .form {\n    flex: 1;\n    overflow-y: auto;\n    padding-bottom: calc(96px + env(safe-area-inset-bottom));\n  }\n  .grid2 { grid-template-columns: 1fr; }\n  .input { font-size: 16px; }\n  .submit {\n    position: sticky;\n    bottom: 0;\n    width: 100%;\n    margin-top: 0;\n    border-radius: 12px;\n    padding: 14px 18px;\n    min-height: 44px;\n    box-shadow: 0 -1px 0 rgba(44,44,39,0.10);\n    margin-bottom: calc(12px + env(safe-area-inset-bottom));\n  }\n}\n\n@keyframes sheetIn {\n  from { opacity: 0; transform: translateY(12px); }\n  to { opacity: 1; transform: translateY(0); }\n}\n"
      ]
    },

    "CallbackModal.module.css": {
      "intent": "Full-screen sheet like AuthModal; textarea + consent; sticky submit.",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .backdrop { padding: 0; align-items: stretch; justify-content: stretch; }\n  .modal {\n    width: 100vw; height: 100vh; max-width: none;\n    border-radius: 0; padding: 16px 20px 0;\n    display: flex; flex-direction: column; overflow: hidden;\n    animation: sheetIn var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n  }\n  .close { top: 10px; right: 10px; width: 44px; height: 44px; }\n  .header { margin-bottom: 12px; padding-right: 44px; }\n  .iconWrap { width: 44px; height: 44px; border-radius: 12px; background: #aebb50; }\n  .title { font-size: 20px; }\n  .form {\n    flex: 1; overflow-y: auto;\n    padding-bottom: calc(96px + env(safe-area-inset-bottom));\n  }\n  .input, .textarea { font-size: 16px; }\n  .submit {\n    position: sticky; bottom: 0; width: 100%;\n    min-height: 44px; border-radius: 12px;\n    margin: 0 0 calc(12px + env(safe-area-inset-bottom));\n  }\n}\n"
      ]
    },

    "CartDrawer.module.css": {
      "intent": "Right drawer on desktop -> bottom-sheet or full-screen on mobile. Use full-screen for cart to avoid cramped checkout.",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .drawer {\n    left: 0;\n    right: 0;\n    top: auto;\n    bottom: 0;\n    width: 100vw;\n    height: 100vh;\n    transform: translateY(100%);\n    transition: transform var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n    border-top-left-radius: 0;\n    border-top-right-radius: 0;\n  }\n  .drawerOpen { transform: translateY(0); }\n  .drawerHeader {\n    padding: 16px 20px;\n    height: auto;\n    min-height: 56px;\n    border-bottom: 1px solid rgba(44,44,39,0.10);\n  }\n  .closeBtn, .iconButton { width: 44px; height: 44px; }\n  .fullWrap { padding: 8px 20px 0; }\n  .itemsList { padding-top: 0; }\n  .itemCard { padding: 12px; gap: 12px; }\n  .itemImage { width: 96px; height: 96px; }\n  .itemName { font-size: 16px; }\n  .counterBtn { width: 44px; height: 44px; }\n  .crossSellList { padding-bottom: 8px; }\n  .totalsRow {\n    position: sticky;\n    bottom: 0;\n    background: var(--bg-cream, #f9f7f2);\n    padding-bottom: calc(12px + env(safe-area-inset-bottom));\n  }\n  .checkoutBtn { min-height: 44px; }\n  .emptyInner { padding: 24px 20px 0; }\n  .emptyCta {\n    margin: 16px 20px calc(16px + env(safe-area-inset-bottom));\n    min-height: 44px;\n  }\n}\n"
      ]
    },

    "PaymentConfirmModal.module.css": {
      "intent": "Centered desktop modal -> full-screen sheet on mobile with sticky action buttons.",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .backdrop { padding: 0; align-items: stretch; justify-content: stretch; overflow: hidden; }\n  .modal {\n    width: 100vw; height: 100vh; max-width: none;\n    border-radius: 0; padding: 16px 20px 0;\n    display: flex; flex-direction: column; overflow: hidden;\n    animation: sheetIn var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n  }\n  .close { top: 10px; right: 10px; width: 44px; height: 44px; }\n  .stepper {\n    margin: 0 0 12px;\n    overflow-x: auto;\n    -webkit-overflow-scrolling: touch;\n    padding-bottom: 6px;\n  }\n  .title { font-size: 18px; }\n  .reqRow { grid-template-columns: 110px 1fr auto; }\n  .reqValue { font-size: 13px; }\n  .actions {\n    position: sticky;\n    bottom: 0;\n    background: var(--agro-cream, #f9f7f2);\n    padding: 12px 0 calc(12px + env(safe-area-inset-bottom));\n    border-top: 1px solid rgba(44,44,39,0.10);\n    margin-top: auto;\n  }\n  .btnGhost, .btnPrimary {\n    width: 100%;\n    min-height: 44px;\n  }\n  .actions { flex-direction: column-reverse; gap: 10px; }\n  .input { font-size: 16px; }\n}\n"
      ]
    },

    "EmailModal.module.css": {
      "intent": "Already has small breakpoint; extend to full-screen sheet at <=768.",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .backdrop { padding: 0; align-items: stretch; justify-content: stretch; }\n  .modal {\n    width: 100vw; height: 100vh; max-width: none;\n    max-height: none;\n    border-radius: 0;\n    padding: 16px 20px 0;\n    overflow: hidden;\n    display: flex;\n    flex-direction: column;\n    animation: sheetIn var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n  }\n  .close { top: 10px; right: 10px; width: 44px; height: 44px; }\n  .header { margin-bottom: 12px; padding-right: 44px; }\n  .iconWrap { width: 44px; height: 44px; background: #aebb50; }\n  .title { font-size: 20px; }\n  .form {\n    flex: 1; overflow-y: auto;\n    padding-bottom: calc(96px + env(safe-area-inset-bottom));\n  }\n  .row2 { grid-template-columns: 1fr; }\n  .input, .textarea { font-size: 16px; }\n  .submit {\n    position: sticky; bottom: 0; width: 100%;\n    min-height: 44px; border-radius: 12px;\n    margin: 0 0 calc(12px + env(safe-area-inset-bottom));\n  }\n}\n"
      ]
    },

    "PolicyModal.module.css": {
      "intent": "Legal text modal -> full-screen overlay with scrollable body on mobile.",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .backdrop { padding: 0; align-items: stretch; justify-content: stretch; }\n  .modal {\n    width: 100vw; height: 100vh; max-height: 100vh;\n    border-radius: 0;\n    animation: sheetIn var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n  }\n  .header {\n    padding: 16px 20px;\n    position: sticky;\n    top: 0;\n    z-index: 2;\n  }\n  .close { width: 44px; height: 44px; padding: 0; border-radius: 12px; }\n  .content { padding: 16px 20px 24px; font-size: 15px; }\n  .footer {\n    position: sticky;\n    bottom: 0;\n    padding: 12px 20px calc(12px + env(safe-area-inset-bottom));\n    z-index: 2;\n  }\n  .acceptBtn { width: 100%; min-height: 44px; }\n}\n"
      ]
    },

    "confirm-modal.module.css": {
      "intent": "Centered confirm card on desktop -> bottom-sheet on mobile (full-width).",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .backdrop {\n    align-items: flex-end;\n    justify-content: stretch;\n    padding: 0;\n  }\n  .modal {\n    width: 100vw;\n    max-width: none;\n    border-radius: 16px 16px 0 0;\n    padding: 16px 20px 12px;\n    box-shadow: 0 -10px 30px rgba(15,26,20,.18);\n    animation: sheetUp var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n  }\n  .actions {\n    display: grid;\n    grid-template-columns: 1fr;\n    gap: 10px;\n    padding-bottom: calc(12px + env(safe-area-inset-bottom));\n  }\n  .cancelBtn, .confirmBtn, .dangerBtn {\n    width: 100%;\n    min-height: 44px;\n  }\n}\n\n@keyframes sheetUp {\n  from { transform: translateY(12px); opacity: 0; }\n  to { transform: translateY(0); opacity: 1; }\n}\n"
      ]
    },

    "UserDrawer.module.css": {
      "intent": "Right drawer on desktop -> full-screen sheet on mobile.",
      "add_or_update": [
        "@media (max-width: 768px) {\n  .drawer {\n    left: 0;\n    right: 0;\n    width: 100vw;\n    max-width: none;\n    transform: translateY(100%);\n    transition: transform var(--dur-sheet, 240ms) var(--ease-sheet, cubic-bezier(0.2,0.8,0.2,1));\n    box-shadow: 0 -10px 30px rgba(15,26,20,.18);\n  }\n  .drawerOpen { transform: translateY(0); }\n  .drawerHeader {\n    padding: 16px 20px;\n    min-height: 56px;\n  }\n  .closeBtn { width: 44px; height: 44px; }\n  .userBlock { padding: 16px 20px; }\n  .nav { padding: 8px 12px; }\n  .navItem {\n    min-height: 44px;\n    padding: 12px 14px;\n  }\n  .logoutBtn {\n    min-height: 44px;\n    margin: 12px 16px calc(16px + env(safe-area-inset-bottom));\n  }\n}\n"
      ]
    }
  },

  "profile_mobile_blueprint": {
    "profile_layout": {
      "desktop": "Sidebar nav (280px) + content",
      "mobile": {
        "pattern": "Horizontal scroll pill tabs with scroll-snap; optional overflow hint",
        "css": ".profileTabs {\n  display: flex;\n  gap: 8px;\n  overflow-x: auto;\n  -webkit-overflow-scrolling: touch;\n  scroll-snap-type: x mandatory;\n  padding: 0 20px;\n}\n.profileTab {\n  scroll-snap-align: start;\n  flex: 0 0 auto;\n  white-space: nowrap;\n  min-height: 44px;\n  padding: 10px 14px;\n  border-radius: 999px;\n  border: 1px solid rgba(44,44,39,0.14);\n  background: #fff;\n  color: #2c2c27;\n  transition: background-color .15s ease, border-color .15s ease;\n}\n.profileTab[data-active='true'] {\n  background: #1b4332;\n  border-color: #1b4332;\n  color: #fff;\n}\n",
        "interaction": "Active tab uses solid dark green; keep chips large for gloves/touch"
      }
    },
    "profile_dashboard": {
      "layout": "2-col grid -> 1-col stack on mobile",
      "rules": [
        "Use card stack with 16px gaps",
        "Card padding on mobile: 20px",
        "Primary actions full-width"
      ]
    },
    "orders": {
      "desktop": "Table-like rows",
      "mobile": "Card list (already implemented in profile.module.css orderCard*)",
      "mobile_rules": [
        "Hide table header at <=900px (already)",
        "Ensure action buttons stack full-width (already at <=720px)",
        "Ensure tap targets >=44px for track/repeat buttons (set min-height:44px if needed)"
      ]
    },
    "addresses": {
      "mobile_rules": [
        "Header row becomes vertical stack: title then full-width add button",
        "Address actions become icon buttons or stacked links with >=44px hit area",
        "Add/Edit modal should become full-screen sheet on <=768px (currently centered)"
      ],
      "addresses_modal_mobile_css": "@media (max-width: 768px) {\n  .modalBackdrop { padding: 0; align-items: stretch; justify-content: stretch; }\n  .modal {\n    width: 100vw;\n    max-width: none;\n    height: 100vh;\n    max-height: 100vh;\n    border-radius: 0;\n    padding: 16px 20px 0;\n    overflow: hidden;\n    display: flex;\n    flex-direction: column;\n    transform: none;\n  }\n  .modalActions {\n    position: sticky;\n    bottom: 0;\n    background: #fff;\n    padding: 12px 0 calc(12px + env(safe-area-inset-bottom));\n    border-top: 1px solid rgba(44,44,39,0.10);\n    margin-top: auto;\n  }\n  .modalBtn { width: 100%; min-height: 44px; }\n  .modalActions { flex-direction: column-reverse; }\n  .fieldInput { font-size: 16px; }\n  .carrierTabs {\n    width: 100%;\n    display: grid;\n    grid-template-columns: 1fr 1fr;\n  }\n  .carrierTab { min-height: 44px; }\n}\n"
    }
  },

  "component_path": {
    "shadcn_primary": [
      "/app/frontend/src/components/ui/dialog.jsx",
      "/app/frontend/src/components/ui/drawer.jsx",
      "/app/frontend/src/components/ui/sheet.jsx",
      "/app/frontend/src/components/ui/button.jsx",
      "/app/frontend/src/components/ui/input.jsx",
      "/app/frontend/src/components/ui/textarea.jsx",
      "/app/frontend/src/components/ui/checkbox.jsx",
      "/app/frontend/src/components/ui/tabs.jsx",
      "/app/frontend/src/components/ui/badge.jsx",
      "/app/frontend/src/components/ui/scroll-area.jsx"
    ],
    "note": "Current modals are CSS-module based; keep them, but align behavior with shadcn patterns (sheet/drawer) for future refactor."
  },

  "instructions_to_main_agent": [
    "Do NOT touch Navbar1 and Footer1.",
    "Implement mobile sheet behavior via CSS @media (max-width:768px) in each listed module file using selectors that already exist (.backdrop, .modal, .drawer, etc.).",
    "Ensure every close button / CTA / tab / input has data-testid (many already do; add missing ones in modal components if needed).",
    "Ensure tap targets: set width/height/min-height to 44px for icon buttons and primary CTAs on mobile.",
    "Prevent iOS zoom: set input/textarea font-size: 16px in mobile rules.",
    "Sticky footer: use padding-bottom: calc(12px + env(safe-area-inset-bottom)).",
    "Avoid horizontal overflow: set max-width:100%, min-width:0 on flex children; avoid fixed widths on mobile.",
    "No transition: all. Only transition background-color, border-color, box-shadow, opacity, transform (for sheet only).",
    "Add body scroll lock when any modal/drawer opens (JS in modal components)."
  ],

  "image_urls": {
    "note": "No new imagery required for this task (UI refactor only)."
  },

  "accessibility": {
    "rules": [
      "All dialogs must have role=dialog and aria-modal=true (already in addresses modal).",
      "Close button must be reachable and have aria-label.",
      "Focus-visible rings: use olive (#aebb50) or green (#1b4332) with sufficient contrast.",
      "Ensure scrollable body inside sheet; do not trap scroll behind backdrop.",
      "Respect prefers-reduced-motion: reduce sheet animation duration."
    ]
  },

  "motion": {
    "sheet": {
      "duration": "240ms",
      "easing": "cubic-bezier(0.2, 0.8, 0.2, 1)",
      "properties": ["transform", "opacity"],
      "avoid": ["transition: all"]
    },
    "controls": {
      "duration": "120–180ms",
      "properties": ["background-color", "border-color", "box-shadow", "opacity"]
    }
  },

  "appendix_general_ui_ux_design_guidelines": "<General UI UX Design Guidelines>\n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
