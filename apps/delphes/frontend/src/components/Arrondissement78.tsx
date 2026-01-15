"use client";

import { useState, useMemo, useRef, useEffect, KeyboardEvent } from "react";
import { useLanguage } from "@/contexts/LanguageContext";

// Mapping des codes postaux vers les communes (structure simplifiée pour les principales communes)
// Note: Certaines communes peuvent avoir plusieurs codes postaux
const codePostalToCommune: Record<string, string> = {
    // Versailles et environs (78xxx)
    "78000": "VERSAILLES", "78100": "SAINT GERMAIN EN LAYE", "78110": "LE VESINET",
    "78120": "RAMBOUILLET", "78130": "LES MUREAUX", "78140": "VELIZY VILLACOUBLAY",
    "78150": "LE CHESNAY", "78160": "MARLY LE ROI", "78170": "LA CELLE ST CLOUD",
    "78180": "MONTIGNY LE BRETONNEUX", "78190": "TRAPPES", "78200": "MANTES LA JOLIE",
    "78210": "SAINT CYR L'ECOLE", "78220": "VIROFLAY", "78230": "LE PECQ",
    "78240": "CHAMBOURCY", "78250": "MEULAN-EN-YVELINES", "78260": "ACHERES",
    "78270": "BONNIERES SUR SEINE", "78280": "GUYANCOURT", "78290": "CROISSY SUR SEINE",
    "78300": "POISSY", "78310": "MAISONS LAFFITTE", "78320": "LE MESNIL ST DENIS",
    "78330": "FONTENAY LE FLEURY", "78340": "LES CLAYES SOUS BOIS", "78350": "JOUY EN JOSAS",
    "78360": "MONTESSON", "78370": "PLAISIR", "78380": "BOUGIVAL",
    "78390": "BOIS D'ARCY", "78400": "CHATOU", "78410": "AUBERGENVILLE",
    "78420": "CARRIERES SUR SEINE", "78430": "LOUVECIENNES", "78440": "GARGENVILLE",
    "78450": "VILLEPREUX", "78460": "CHEVREUSE", "78470": "MAGNY LES HAMEAUX",
    "78480": "VERNEUIL SUR SEINE", "78490": "GALLUIS", "78500": "SARTROUVILLE",
    "78510": "TRIEL SUR SEINE", "78520": "LIMAY", "78530": "BUCHLAY",
    "78540": "VERNOUILLET", "78550": "HOUDAN", "78560": "PORCHEVILLE",
    "78570": "ANDRESY", "78580": "BAZEMONT", "78590": "NOISY LE ROI",
    "78600": "MAULE", "78610": "SAINT LEGER EN YVELINES", "78620": "L'ETANG LA VILLE",
    "78630": "ORGEVAL", "78640": "NEZEL", "78650": "BEYNES",
    "78660": "ABLIS", "78670": "VILLENNES SUR SEINE", "78680": "EPONE",
    "78690": "LES ESSARTS LE ROI", "78700": "CONFLANS STE HONORINE", "78710": "ROSNY SUR SEINE",
    "78720": "DAMPIERRE EN YVELINES", "78730": "ROCHEFORT EN YVELINES", "78740": "VECQ",
    "78750": "ST REMY L'HONORE", "78760": "JOUARS PONTCHARTRAIN", "78770": "THOIRY",
    "78780": "MAURECOURT", "78790": "MONDREVILLE", "78800": "HOUILLES",
    "78810": "DAVRON", "78820": "JUZIERS", "78830": "BONNELLES",
    "78840": "MOISSON", "78850": "THIVERVAL GRIGNON", "78860": "ST NOM LA BRETECHE",
    "78870": "BAILLY", "78880": "HARDRICOURT", "78890": "GOMECOURT",
    "78910": "ORGERUS", "78920": "ECQUEVILLY", "78930": "GUERVILLE",
    "78940": "LA QUEUE LES YVELINES", "78950": "GAMBAIS", "78955": "CARRIERES SOUS POISSY",
    "78960": "VOISINS LE BRETONNEUX", "78970": "MEZIERES SUR SEINE", "78980": "LE TERTRE ST DENIS",
    "78990": "ELANCOURT",
};

// Données des communes des Yvelines avec leur arrondissement de rattachement et code postal
// Source: Arrondissements de rattachement des communes des Yvelines - 1er janvier 2017
// Codes postaux: source La Poste (enrichissement progressif)
export const communesYvelines: Array<{ commune: string; arrondissement: string; codePostal?: string }> = [
    { commune: "ABLIS", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "ACHERES", arrondissement: "Saint-Germain-en-Laye", codePostal: "78260" },
    { commune: "ADAINVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "AIGREMONT", arrondissement: "Saint-Germain-en-Laye", codePostal: "78240" },
    { commune: "ALLAINVILLE", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "ALLUETS LE ROI (LES)", arrondissement: "Saint-Germain-en-Laye", codePostal: "78580" },
    { commune: "ANDELU", arrondissement: "Saint-Germain-en-Laye", codePostal: "78580" },
    { commune: "ANDRESY", arrondissement: "Saint-Germain-en-Laye", codePostal: "78570" },
    { commune: "ARNOUVILLE LES MANTES", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "AUBERGENVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78410" },
    { commune: "AUFFARGIS", arrondissement: "Rambouillet", codePostal: "78610" },
    { commune: "AUFFREVILLE BRASSEUIL", arrondissement: "Mantes-la-Jolie", codePostal: "78930" },
    { commune: "AULNAY SUR MAULDRE", arrondissement: "Mantes-la-Jolie", codePostal: "78126" },
    { commune: "AUTEUIL LE ROI", arrondissement: "Rambouillet", codePostal: "78770" },
    { commune: "AUTOUILLET", arrondissement: "Rambouillet", codePostal: "78770" },
    { commune: "BAILLY", arrondissement: "Versailles", codePostal: "78870" },
    { commune: "BAZAINVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78550" },
    { commune: "BAZEMONT", arrondissement: "Saint-Germain-en-Laye", codePostal: "78580" },
    { commune: "BAZOCHES SUR GUYONNE", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "BEHOUST", arrondissement: "Rambouillet", codePostal: "78910" },
    { commune: "BENNECOURT", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "BEYNES", arrondissement: "Rambouillet", codePostal: "78650" },
    { commune: "BLARU", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "BOINVILLE EN MANTOIS", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "BOINVILLE LE GAILLARD", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "BOINVILLIERS", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "BOIS D'ARCY", arrondissement: "Versailles", codePostal: "78390" },
    { commune: "BOISSETS", arrondissement: "Mantes-la-Jolie", codePostal: "78910" },
    { commune: "BOISSIERE ECOLE (LA)", arrondissement: "Rambouillet", codePostal: "78610" },
    { commune: "BOISSY MAUVOISIN", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "BOISSY SANS AVOIR", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "BONNELLES", arrondissement: "Rambouillet", codePostal: "78830" },
    { commune: "BONNIERES SUR SEINE", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "BOUAFLE", arrondissement: "Mantes-la-Jolie", codePostal: "78410" },
    { commune: "BOUGIVAL", arrondissement: "Versailles", codePostal: "78380" },
    { commune: "BOURDONNE", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "BREUIL BOIS ROBERT", arrondissement: "Mantes-la-Jolie", codePostal: "78930" },
    { commune: "BREVAL", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "BREVIAIRES (LES)", arrondissement: "Rambouillet", codePostal: "78610" },
    { commune: "BRUEIL EN VEXIN", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "BUC", arrondissement: "Versailles", codePostal: "78530" },
    { commune: "BUCHELAY", arrondissement: "Mantes-la-Jolie", codePostal: "78530" },
    { commune: "BULLION", arrondissement: "Rambouillet", codePostal: "78830" },
    { commune: "CARRIERES SOUS POISSY", arrondissement: "Saint-Germain-en-Laye", codePostal: "78955" },
    { commune: "CARRIERES SUR SEINE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78420" },
    { commune: "CELLE LES BORDES (LA)", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "CELLE ST CLOUD (LA)", arrondissement: "Versailles", codePostal: "78170" },
    { commune: "CERNAY LA VILLE", arrondissement: "Rambouillet", codePostal: "78720" },
    { commune: "CHAMBOURCY", arrondissement: "Saint-Germain-en-Laye", codePostal: "78240" },
    { commune: "CHANTELOUP LES VIGNES", arrondissement: "Saint-Germain-en-Laye", codePostal: "78570" },
    { commune: "CHAPET", arrondissement: "Mantes-la-Jolie", codePostal: "78130" },
    { commune: "CHATEAUFORT", arrondissement: "Versailles", codePostal: "78117" },
    { commune: "CHATOU", arrondissement: "Saint-Germain-en-Laye", codePostal: "78400" },
    { commune: "CHAUFOUR LES BONNIERES", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "CHAVENAY", arrondissement: "Saint-Germain-en-Laye", codePostal: "78450" },
    { commune: "CHESNAY (LE)", arrondissement: "Versailles", codePostal: "78150" },
    { commune: "CHEVREUSE", arrondissement: "Rambouillet", codePostal: "78460" },
    { commune: "CHOISEL", arrondissement: "Rambouillet", codePostal: "78460" },
    { commune: "CIVRY LA FORET", arrondissement: "Mantes-la-Jolie", codePostal: "78910" },
    { commune: "CLAIREFONTAINE", arrondissement: "Rambouillet", codePostal: "78120" },
    { commune: "CLAYES SOUS BOIS (LES)", arrondissement: "Versailles", codePostal: "78340" },
    { commune: "COIGNIERES", arrondissement: "Rambouillet", codePostal: "78310" },
    { commune: "CONDE SUR VESGRE", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "CONFLANS STE HONORINE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78700" },
    { commune: "COURGENT", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "CRAVENT", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "CRESPIERES", arrondissement: "Saint-Germain-en-Laye", codePostal: "78121" },
    { commune: "CROISSY SUR SEINE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78290" },
    { commune: "DAMMARTIN EN SERVE", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "DAMPIERRE EN YVELINES", arrondissement: "Rambouillet", codePostal: "78720" },
    { commune: "DANNEMARIE", arrondissement: "Mantes-la-Jolie", codePostal: "78550" },
    { commune: "DAVRON", arrondissement: "Saint-Germain-en-Laye", codePostal: "78810" },
    { commune: "DROCOURT", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "ECQUEVILLY", arrondissement: "Mantes-la-Jolie", codePostal: "78920" },
    { commune: "ELANCOURT", arrondissement: "Rambouillet", codePostal: "78990" },
    { commune: "EMANCE", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "EPONE", arrondissement: "Mantes-la-Jolie", codePostal: "78680" },
    { commune: "ESSARTS LE ROI (LES)", arrondissement: "Rambouillet", codePostal: "78690" },
    { commune: "ETANG LA VILLE (L')", arrondissement: "Saint-Germain-en-Laye", codePostal: "78620" },
    { commune: "EVECQUEMONT", arrondissement: "Mantes-la-Jolie", codePostal: "78740" },
    { commune: "FALAISE (LA)", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "FAVRIEUX", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "FEUCHEROLLES", arrondissement: "Saint-Germain-en-Laye", codePostal: "78112" },
    { commune: "FLACOURT", arrondissement: "Mantes-la-Jolie", codePostal: "78250" },
    { commune: "FLEXANVILLE", arrondissement: "Rambouillet", codePostal: "78910" },
    { commune: "FLINS NEUVE EGLISE", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "FLINS SUR SEINE", arrondissement: "Mantes-la-Jolie", codePostal: "78410" },
    { commune: "FOLLAINVILLE DENNEMONT", arrondissement: "Mantes-la-Jolie", codePostal: "78520" },
    { commune: "FONTENAY LE FLEURY", arrondissement: "Versailles", codePostal: "78330" },
    { commune: "FONTENAY MAUVOISIN", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "FONTENAY SAINT PERE", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "FOURQUEUX", arrondissement: "Saint-Germain-en-Laye", codePostal: "78112" },
    { commune: "FRENEUSE", arrondissement: "Mantes-la-Jolie", codePostal: "78840" },
    { commune: "GAILLON SUR MONTCIENT", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "GALLUIS", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "GAMBAIS", arrondissement: "Rambouillet", codePostal: "78950" },
    { commune: "GAMBAISEUL", arrondissement: "Rambouillet", codePostal: "78950" },
    { commune: "GARANCIERES", arrondissement: "Rambouillet", codePostal: "78890" },
    { commune: "GARGENVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "GAZERAN", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "GOMMECOURT", arrondissement: "Mantes-la-Jolie", codePostal: "78890" },
    { commune: "GOUPILLIERES", arrondissement: "Rambouillet", codePostal: "78113" },
    { commune: "GOUSSONVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78930" },
    { commune: "GRANDCHAMP", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "GRESSEY", arrondissement: "Mantes-la-Jolie", codePostal: "78550" },
    { commune: "GROSROUVRE", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "GUERNES", arrondissement: "Mantes-la-Jolie", codePostal: "78580" },
    { commune: "GUERVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78930" },
    { commune: "GUITRANCOURT", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "GUYANCOURT", arrondissement: "Versailles", codePostal: "78280" },
    { commune: "HARDRICOURT", arrondissement: "Mantes-la-Jolie", codePostal: "78880" },
    { commune: "HARGEVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "HAUTEVILLE (LA)", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "HERBEVILLE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78580" },
    { commune: "HERMERAY", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "HOUDAN", arrondissement: "Mantes-la-Jolie", codePostal: "78550" },
    { commune: "HOUILLES", arrondissement: "Saint-Germain-en-Laye", codePostal: "78800" },
    { commune: "ISSOU", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "JAMBVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "JEUFOSSE", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "JOUARS PONTCHARTRAIN", arrondissement: "Rambouillet", codePostal: "78760" },
    { commune: "JOUY EN JOSAS", arrondissement: "Versailles", codePostal: "78350" },
    { commune: "JOUY MAUVOISIN", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "JUMEAUVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78580" },
    { commune: "JUZIERS", arrondissement: "Mantes-la-Jolie", codePostal: "78820" },
    { commune: "LAINVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78440" },
    { commune: "LEVIS ST NOM", arrondissement: "Rambouillet", codePostal: "78320" },
    { commune: "LIMAY", arrondissement: "Mantes-la-Jolie", codePostal: "78520" },
    { commune: "LIMETZ VILLEZ", arrondissement: "Mantes-la-Jolie", codePostal: "78420" },
    { commune: "LOGES EN JOSAS (LES)", arrondissement: "Versailles", codePostal: "78350" },
    { commune: "LOMMOYE", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "LONGNES", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "LONGVILLIERS", arrondissement: "Rambouillet", codePostal: "78730" },
    { commune: "LOUVECIENNES", arrondissement: "Saint-Germain-en-Laye", codePostal: "78430" },
    { commune: "MAGNANVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "MAGNY LES HAMEAUX", arrondissement: "Rambouillet", codePostal: "78470" },
    { commune: "MAISONS LAFFITTE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78310" },
    { commune: "MANTES LA JOLIE", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "MANTES LA VILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "MARCQ", arrondissement: "Rambouillet", codePostal: "78770" },
    { commune: "MAREIL LE GUYON", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "MAREIL MARLY", arrondissement: "Saint-Germain-en-Laye", codePostal: "78124" },
    { commune: "MAREIL SUR MAULDRE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78126" },
    { commune: "MARLY LE ROI", arrondissement: "Saint-Germain-en-Laye", codePostal: "78160" },
    { commune: "MAULE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78580" },
    { commune: "MAULETTE", arrondissement: "Mantes-la-Jolie", codePostal: "78550" },
    { commune: "MAURECOURT", arrondissement: "Saint-Germain-en-Laye", codePostal: "78780" },
    { commune: "MAUREPAS", arrondissement: "Rambouillet", codePostal: "78310" },
    { commune: "MEDAN", arrondissement: "Saint-Germain-en-Laye", codePostal: "78470" },
    { commune: "MENERVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "MERE", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "MERICOURT", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "MESNIL LE ROI (LE)", arrondissement: "Saint-Germain-en-Laye", codePostal: "78600" },
    { commune: "MESNIL ST DENIS (LE)", arrondissement: "Rambouillet", codePostal: "78320" },
    { commune: "MESNULS (LES)", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "MEULAN-EN-YVELINES", arrondissement: "Mantes-la-Jolie", codePostal: "78250" },
    { commune: "MEZIERES SUR SEINE", arrondissement: "Mantes-la-Jolie", codePostal: "78970" },
    { commune: "MEZY SUR SEINE", arrondissement: "Mantes-la-Jolie", codePostal: "78250" },
    { commune: "MILLEMONT", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "MILON LA CHAPELLE", arrondissement: "Rambouillet", codePostal: "78470" },
    { commune: "MITTAINVILLE", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "MOISSON", arrondissement: "Mantes-la-Jolie", codePostal: "78840" },
    { commune: "MONDREVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "MONTAINVILLE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78112" },
    { commune: "MONTALET LE BOIS", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "MONTCHAUVET", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "MONTESSON", arrondissement: "Saint-Germain-en-Laye", codePostal: "78360" },
    { commune: "MONTFORT L'AMAURY", arrondissement: "Rambouillet", codePostal: "78490" },
    { commune: "MONTIGNY LE BRETONNEUX", arrondissement: "Versailles", codePostal: "78180" },
    { commune: "MORAINVILLIERS", arrondissement: "Saint-Germain-en-Laye", codePostal: "78930" },
    { commune: "MOUSSEAUX SUR SEINE", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "MULCENT", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "MUREAUX (LES)", arrondissement: "Mantes-la-Jolie", codePostal: "78130" },
    { commune: "NEAUPHLE LE CHATEAU", arrondissement: "Rambouillet", codePostal: "78640" },
    { commune: "NEAUPHLE LE VIEUX", arrondissement: "Rambouillet", codePostal: "78640" },
    { commune: "NEAUPHLETTE", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "NEZEL", arrondissement: "Mantes-la-Jolie", codePostal: "78640" },
    { commune: "NOISY LE ROI", arrondissement: "Versailles", codePostal: "78590" },
    { commune: "OINVILLE SUR MONTCIENT", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "ORCEMONT", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "ORGERUS", arrondissement: "Mantes-la-Jolie", codePostal: "78910" },
    { commune: "ORGEVAL", arrondissement: "Saint-Germain-en-Laye", codePostal: "78630" },
    { commune: "ORPHIN", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "ORSONVILLE", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "ORVILLIERS", arrondissement: "Mantes-la-Jolie", codePostal: "78910" },
    { commune: "OSMOY", arrondissement: "Mantes-la-Jolie", codePostal: "78910" },
    { commune: "PARAY DOUAVILLE", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "PECQ (LE)", arrondissement: "Saint-Germain-en-Laye", codePostal: "78230" },
    { commune: "PERDREAUVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "PERRAY EN YVELINES (LE)", arrondissement: "Rambouillet", codePostal: "78610" },
    { commune: "PLAISIR", arrondissement: "Versailles", codePostal: "78370" },
    { commune: "POIGNY LA FORET", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "POISSY", arrondissement: "Saint-Germain-en-Laye", codePostal: "78300" },
    { commune: "PONTHEVRARD", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "PORCHEVILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78560" },
    { commune: "PORT MARLY (LE)", arrondissement: "Saint-Germain-en-Laye", codePostal: "78560" },
    { commune: "PORT VILLEZ", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "PRUNAY EN YVELINES", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "PRUNAY LE TEMPLE", arrondissement: "Mantes-la-Jolie", codePostal: "78910" },
    { commune: "QUEUE LES YVELINES (LA)", arrondissement: "Rambouillet", codePostal: "78940" },
    { commune: "RAIZEUX", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "RAMBOUILLET", arrondissement: "Rambouillet", codePostal: "78120" },
    { commune: "RENNEMOULIN", arrondissement: "Versailles", codePostal: "78530" },
    { commune: "RICHEBOURG", arrondissement: "Mantes-la-Jolie", codePostal: "78550" },
    { commune: "ROCHEFORT EN YVELINES", arrondissement: "Rambouillet", codePostal: "78730" },
    { commune: "ROCQUENCOURT", arrondissement: "Versailles", codePostal: "78150" },
    { commune: "ROLLEBOISE", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "ROSAY", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "ROSNY SUR SEINE", arrondissement: "Mantes-la-Jolie", codePostal: "78710" },
    { commune: "SAILLY", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "SAINT ARNOULT EN YVELINES", arrondissement: "Rambouillet", codePostal: "78730" },
    { commune: "SAINT CYR L'ECOLE", arrondissement: "Versailles", codePostal: "78210" },
    { commune: "SAINT FORGET", arrondissement: "Rambouillet", codePostal: "78730" },
    { commune: "SAINT GERMAIN DE LA GRANGE", arrondissement: "Rambouillet", codePostal: "78610" },
    { commune: "SAINT GERMAIN EN LAYE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78100" },
    { commune: "SAINT HILARION", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "SAINT ILLIERS LA VILLE", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "SAINT ILLIERS LE BOIS", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "SAINT LAMBERT DES BOIS", arrondissement: "Rambouillet", codePostal: "78470" },
    { commune: "SAINT LEGER EN YVELINES", arrondissement: "Rambouillet", codePostal: "78610" },
    { commune: "SAINT MARTIN DE BRETHENCOURT", arrondissement: "Rambouillet", codePostal: "78660" },
    { commune: "SAINT MARTIN DES CHAMPS", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "SAINT MARTIN LA GARENNE", arrondissement: "Mantes-la-Jolie", codePostal: "78520" },
    { commune: "SAINT NOM LA BRETECHE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78860" },
    { commune: "SAINT REMY LES CHEVREUSE", arrondissement: "Rambouillet", codePostal: "78470" },
    { commune: "SAINT REMY L'HONORE", arrondissement: "Rambouillet", codePostal: "78750" },
    { commune: "SAINTE MESME", arrondissement: "Rambouillet", codePostal: "78730" },
    { commune: "SARTROUVILLE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78500" },
    { commune: "SAULX MARCHAIS", arrondissement: "Rambouillet", codePostal: "78650" },
    { commune: "SENLISSE", arrondissement: "Rambouillet", codePostal: "78720" },
    { commune: "SEPTEUIL", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "SOINDRES", arrondissement: "Mantes-la-Jolie", codePostal: "78200" },
    { commune: "SONCHAMP", arrondissement: "Rambouillet", codePostal: "78120" },
    { commune: "TACOIGNIERES", arrondissement: "Mantes-la-Jolie", codePostal: "78910" },
    { commune: "TARTRE GAUDRAN (LE)", arrondissement: "Mantes-la-Jolie", codePostal: "78113" },
    { commune: "TERTRE ST DENIS (LE)", arrondissement: "Mantes-la-Jolie", codePostal: "78980" },
    { commune: "TESSANCOURT SUR AUBETTE", arrondissement: "Mantes-la-Jolie", codePostal: "78250" },
    { commune: "THIVERVAL GRIGNON", arrondissement: "Rambouillet", codePostal: "78850" },
    { commune: "THOIRY", arrondissement: "Rambouillet", codePostal: "78770" },
    { commune: "TILLY", arrondissement: "Mantes-la-Jolie", codePostal: "78790" },
    { commune: "TOUSSUS LE NOBLE", arrondissement: "Versailles", codePostal: "78117" },
    { commune: "TRAPPES", arrondissement: "Versailles", codePostal: "78190" },
    { commune: "TREMBLAY SUR MAULDRE (LE)", arrondissement: "Rambouillet", codePostal: "78113" },
    { commune: "TRIEL SUR SEINE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78510" },
    { commune: "VAUX SUR SEINE", arrondissement: "Mantes-la-Jolie", codePostal: "78740" },
    { commune: "VELIZY VILLACOUBLAY", arrondissement: "Versailles", codePostal: "78140" },
    { commune: "VERNEUIL SUR SEINE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78480" },
    { commune: "VERNOUILLET", arrondissement: "Saint-Germain-en-Laye", codePostal: "78540" },
    { commune: "VERRIERE (LA)", arrondissement: "Rambouillet", codePostal: "78630" },
    { commune: "VERSAILLES", arrondissement: "Versailles", codePostal: "78000" },
    { commune: "VERT", arrondissement: "Mantes-la-Jolie", codePostal: "78930" },
    { commune: "VESINET (LE)", arrondissement: "Saint-Germain-en-Laye", codePostal: "78110" },
    { commune: "VICQ", arrondissement: "Rambouillet", codePostal: "78740" },
    { commune: "VIEILLE EGLISE EN YVELINES", arrondissement: "Rambouillet", codePostal: "78125" },
    { commune: "VILLENEUVE EN CHEVRIE (LA)", arrondissement: "Mantes-la-Jolie", codePostal: "78270" },
    { commune: "VILLENNES SUR SEINE", arrondissement: "Saint-Germain-en-Laye", codePostal: "78670" },
    { commune: "VILLEPREUX", arrondissement: "Versailles", codePostal: "78450" },
    { commune: "VILLETTE", arrondissement: "Mantes-la-Jolie", codePostal: "78930" },
    { commune: "VILLIERS LE MAHIEU", arrondissement: "Rambouillet", codePostal: "78770" },
    { commune: "VILLIERS ST FREDERIC", arrondissement: "Rambouillet", codePostal: "78640" },
    { commune: "VIROFLAY", arrondissement: "Versailles", codePostal: "78220" },
    { commune: "VOISINS LE BRETONNEUX", arrondissement: "Versailles", codePostal: "78960" },
];

// Mapping des arrondissements vers les codes
const arrondissementCodes: Record<string, string> = {
    "Versailles": "VERS",
    "Rambouillet": "RAMB",
    "Saint-Germain-en-Laye": "SGEL",
    "Mantes-la-Jolie": "MLJ",
};

interface Arrondissement78Props {
    value: string;
    onChange: (value: string) => void;
    error?: string;
    initialCommune?: string; // Nom de la commune pour initialisation
}

export default function Arrondissement78({
    value,
    onChange,
    error,
    initialCommune,
}: Arrondissement78Props) {
    const { t } = useLanguage();

    // Clé pour le localStorage
    const STORAGE_KEY = 'arrondissement78-selected-commune';

    // Initialiser avec la commune fournie si disponible, sinon depuis localStorage
    const getInitialCommune = () => {
        // Priorité 1: initialCommune (préremplissage)
        if (initialCommune) {
            const found = communesYvelines.find(c => c.commune === initialCommune);
            return found || null;
        }

        // Priorité 2: localStorage (persistance)
        if (typeof window !== 'undefined') {
            try {
                const savedCommune = localStorage.getItem(STORAGE_KEY);
                if (savedCommune) {
                    const found = communesYvelines.find(c => c.commune === savedCommune);
                    return found || null;
                }
            } catch (e) {
                // Ignorer les erreurs de localStorage (mode privé, etc.)
                console.warn('Impossible d\'accéder au localStorage:', e);
            }
        }

        return null;
    };

    const initialCommuneData = getInitialCommune();
    const [communeInput, setCommuneInput] = useState(initialCommuneData?.commune || "");
    const [selectedCommune, setSelectedCommune] = useState<{ commune: string; arrondissement: string; codePostal?: string } | null>(initialCommuneData);

    const [showSuggestions, setShowSuggestions] = useState(false);
    const [focusedIndex, setFocusedIndex] = useState(-1);
    const [hasNoResults, setHasNoResults] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const suggestionsRef = useRef<HTMLUListElement>(null);
    const suggestionsId = "commune-suggestions-78";
    const inputId = "commune-78";

    // Fonction pour normaliser le nom de commune pour la recherche
    // Gère les articles entre parenthèses (ex: "PECQ (LE)" -> "PECQ" et "LE PECQ")
    const normalizeCommuneForSearch = (communeName: string): string[] => {
        const upperName = communeName.toUpperCase();
        const variants: string[] = [upperName]; // Version originale

        // Extraire l'article entre parenthèses (LE), (LA), (LES), (L')
        const articleMatch = upperName.match(/\(([^)]+)\)/);
        if (articleMatch) {
            const article = articleMatch[1].trim();
            const nameWithoutArticle = upperName.replace(/\s*\([^)]+\)\s*/, '').trim();

            // Ajouter la version avec l'article en début : "LE PECQ"
            variants.push(`${article} ${nameWithoutArticle}`);

            // Ajouter la version sans article : "PECQ"
            variants.push(nameWithoutArticle);
        }

        return variants;
    };

    // Filtrer les communes selon la saisie (par nom de commune OU code postal)
    const filteredCommunes = useMemo(() => {
        if (!communeInput.trim()) {
            setHasNoResults(false);
            return [];
        }
        const searchTerm = communeInput.toUpperCase().trim();

        // Vérifier si c'est un code postal (5 chiffres) ou un début de code postal (chiffres uniquement)
        const isNumeric = /^\d+$/.test(searchTerm);
        const isCodePostalExact = /^\d{5}$/.test(searchTerm);

        if (isCodePostalExact) {
            // Recherche par code postal exact - afficher TOUTES les communes correspondantes
            // Chercher dans les communes avec codePostal
            let filtered = communesYvelines.filter((item) =>
                item.codePostal === searchTerm
            );

            // Si pas de résultat, chercher dans le mapping codePostalToCommune
            if (filtered.length === 0 && codePostalToCommune[searchTerm]) {
                const communeName = codePostalToCommune[searchTerm];
                const found = communesYvelines.find(c => c.commune === communeName);
                if (found) {
                    filtered = [found];
                }
            }

            setHasNoResults(filtered.length === 0);
            // Retourner TOUTES les communes correspondantes (pas de limite pour code postal exact)
            return filtered;
        } else if (isNumeric && searchTerm.length > 0) {
            // Recherche par début de code postal (ex: "78" pour toutes les communes commençant par 78)
            const filtered = communesYvelines.filter((item) =>
                item.codePostal && item.codePostal.startsWith(searchTerm)
            );
            setHasNoResults(filtered.length === 0);
            return filtered.slice(0, 10);
        } else {
            // Recherche par nom de commune (recherche partielle) ou code postal partiel
            // Gère les articles entre parenthèses
            const filtered = communesYvelines.filter((item) => {
                // Recherche dans les variantes normalisées du nom
                const variants = normalizeCommuneForSearch(item.commune);
                const matchesVariant = variants.some(variant => variant.includes(searchTerm));

                // Recherche dans le code postal si disponible
                const matchesCodePostal = item.codePostal && item.codePostal.includes(searchTerm);

                return matchesVariant || matchesCodePostal;
            }).slice(0, 10);

            setHasNoResults(filtered.length === 0 && communeInput.trim().length > 0);
            return filtered;
        }
    }, [communeInput]);

    // Mettre à jour l'arrondissement quand une commune est sélectionnée
    useEffect(() => {
        if (selectedCommune) {
            const code = arrondissementCodes[selectedCommune.arrondissement];
            const newValue = code || "";
            // Ne mettre à jour que si la valeur a changé pour éviter les boucles infinies
            if (newValue !== value) {
                onChange(newValue);
            }
        } else if (!communeInput.trim() && value) {
            // Si aucune commune n'est sélectionnée et le champ est vide, réinitialiser
            onChange("");
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedCommune, communeInput]); // Ne pas inclure onChange et value dans les dépendances

    // Restaurer depuis localStorage au montage si pas d'initialCommune
    useEffect(() => {
        if (!initialCommune && typeof window !== 'undefined') {
            try {
                const savedCommune = localStorage.getItem(STORAGE_KEY);
                if (savedCommune && !selectedCommune) {
                    const found = communesYvelines.find(c => c.commune === savedCommune);
                    if (found) {
                        setSelectedCommune(found);
                        setCommuneInput(found.commune);
                        const code = arrondissementCodes[found.arrondissement];
                        if (code && code !== value) {
                            onChange(code);
                        }
                    }
                }
            } catch (e) {
                // Ignorer les erreurs de localStorage
            }
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []); // Exécuter une seule fois au montage

    // Gérer la sélection d'une commune
    const handleCommuneSelect = (commune: { commune: string; arrondissement: string; codePostal?: string }) => {
        setSelectedCommune(commune);
        // Remplacer par le nom de la commune (pas le code postal)
        setCommuneInput(commune.commune);
        setShowSuggestions(false);
        setFocusedIndex(-1);
        setHasNoResults(false);

        // Sauvegarder dans localStorage
        if (typeof window !== 'undefined') {
            try {
                localStorage.setItem(STORAGE_KEY, commune.commune);
            } catch (e) {
                // Ignorer les erreurs de localStorage
                console.warn('Impossible de sauvegarder dans localStorage:', e);
            }
        }
    };

    // Gérer le changement de saisie
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setCommuneInput(newValue);
        setShowSuggestions(true);
        setFocusedIndex(-1);
        if (!newValue.trim()) {
            setSelectedCommune(null);
            onChange("");
            setHasNoResults(false);

            // Supprimer de localStorage si le champ est vidé
            if (typeof window !== 'undefined') {
                try {
                    localStorage.removeItem(STORAGE_KEY);
                } catch (e) {
                    // Ignorer les erreurs de localStorage
                }
            }
        }
    };

    // Gérer la navigation au clavier (RGAA)
    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (!showSuggestions || filteredCommunes.length === 0) {
            if (e.key === "Enter" && communeInput.trim()) {
                e.preventDefault();
            }
            return;
        }

        switch (e.key) {
            case "ArrowDown":
                e.preventDefault();
                setFocusedIndex((prev) =>
                    prev < filteredCommunes.length - 1 ? prev + 1 : prev
                );
                break;
            case "ArrowUp":
                e.preventDefault();
                setFocusedIndex((prev) => (prev > 0 ? prev - 1 : -1));
                break;
            case "Enter":
                e.preventDefault();
                if (focusedIndex >= 0 && focusedIndex < filteredCommunes.length) {
                    handleCommuneSelect(filteredCommunes[focusedIndex]);
                }
                break;
            case "Escape":
                e.preventDefault();
                setShowSuggestions(false);
                setFocusedIndex(-1);
                inputRef.current?.focus();
                break;
            case "Tab":
                setShowSuggestions(false);
                setFocusedIndex(-1);
                break;
        }
    };

    // Gérer les clics en dehors pour fermer les suggestions
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                suggestionsRef.current &&
                !suggestionsRef.current.contains(event.target as Node) &&
                inputRef.current &&
                !inputRef.current.contains(event.target as Node)
            ) {
                setShowSuggestions(false);
                setFocusedIndex(-1);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // Gérer le focus sur les suggestions pour l'accessibilité
    useEffect(() => {
        if (focusedIndex >= 0 && suggestionsRef.current) {
            const focusedElement = suggestionsRef.current.children[focusedIndex] as HTMLElement;
            if (focusedElement) {
                focusedElement.focus();
            }
        }
    }, [focusedIndex]);

    // Gérer le cas où initialCommune change depuis l'extérieur (ex: préremplissage)
    useEffect(() => {
        if (initialCommune) {
            const found = communesYvelines.find(c => c.commune === initialCommune);
            if (found) {
                setSelectedCommune(found);
                setCommuneInput(found.commune);
                const code = arrondissementCodes[found.arrondissement];
                if (code && code !== value) {
                    onChange(code);
                }
                // Sauvegarder dans localStorage
                if (typeof window !== 'undefined') {
                    try {
                        localStorage.setItem(STORAGE_KEY, found.commune);
                    } catch (e) {
                        // Ignorer les erreurs de localStorage
                    }
                }
            }
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [initialCommune]); // Ne pas inclure onChange et value dans les dépendances

    return (
        <div className="fr-fieldset__element">
            <div className={`fr-input-group ${error ? 'fr-input-group--error' : ''}`}>
                <div className="fr-grid-row fr-grid-row--gutters" style={{ alignItems: 'flex-end' }}>
                    <div className="fr-col-7">
                        <label className="fr-label" htmlFor={inputId}>
                            {t('form.communeDeResidence')} *
                        </label>
                        <div className="fr-input-wrap">
                            <input
                                ref={inputRef}
                                className="fr-input"
                                type="text"
                                id={inputId}
                                name="commune-78"
                                value={communeInput}
                                onChange={handleInputChange}
                                onKeyDown={handleKeyDown}
                                onFocus={() => {
                                    if (communeInput.trim()) {
                                        setShowSuggestions(true);
                                    }
                                }}
                                placeholder={t('form.commune.placeholder')}
                                autoComplete="off"
                                role="combobox"
                                aria-autocomplete="list"
                                aria-controls={suggestionsId}
                                aria-expanded={showSuggestions && filteredCommunes.length > 0}
                                aria-haspopup="listbox"
                                aria-describedby={error ? `${inputId}-error` : undefined}
                                required
                            />
                            {showSuggestions && filteredCommunes.length > 0 && (
                                <ul
                                    ref={suggestionsRef}
                                    id={suggestionsId}
                                    className="fr-list"
                                    role="listbox"
                                    aria-label={t('form.commune.suggestions.label')}
                                    style={{
                                        position: 'absolute',
                                        top: '100%',
                                        left: 0,
                                        right: 0,
                                        zIndex: 1000,
                                        backgroundColor: 'var(--background-default-grey)',
                                        border: '1px solid var(--border-default-grey)',
                                        borderRadius: '0.25rem',
                                        maxHeight: filteredCommunes.length > 10 ? '30rem' : '12.5rem',
                                        overflowY: 'auto',
                                        margin: 0,
                                        padding: 0,
                                        listStyle: 'none',
                                        boxShadow: '0 0.125rem 0.5rem rgba(0, 0, 0, 0.1)',
                                    }}
                                >
                                    {filteredCommunes.map((item, index) => (
                                        <li
                                            key={`${item.commune}-${index}`}
                                            role="option"
                                            aria-selected={focusedIndex === index}
                                            tabIndex={focusedIndex === index ? 0 : -1}
                                            onClick={() => handleCommuneSelect(item)}
                                            onKeyDown={(e: KeyboardEvent<HTMLLIElement>) => {
                                                if (e.key === "Enter" || e.key === " ") {
                                                    e.preventDefault();
                                                    handleCommuneSelect(item);
                                                }
                                            }}
                                            className={focusedIndex === index ? "fr-list__item fr-list__item--selected" : "fr-list__item"}
                                            style={{
                                                padding: '0.5rem 0.75rem',
                                                cursor: 'pointer',
                                                borderBottom: index < filteredCommunes.length - 1 ? '1px solid var(--border-default-grey)' : 'none',
                                                backgroundColor: focusedIndex === index ? 'var(--background-action-low-blue-france)' : 'transparent',
                                            }}
                                        >
                                            {item.commune}{item.codePostal ? ` (${item.codePostal})` : ''}
                                        </li>
                                    ))}
                                </ul>
                            )}
                            {hasNoResults && communeInput.trim() && (
                                <div
                                    className="fr-message fr-message--info fr-mt-1w"
                                    role="status"
                                    aria-live="polite"
                                >
                                    {t('form.commune.noResults')}
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="fr-col-5">
                        <label className="fr-label" htmlFor="arrondissement-display-78">
                            {t('form.arrondissementLabel')}
                        </label>
                        <div className="fr-input-wrap">
                            <input
                                className="fr-input"
                                type="text"
                                id="arrondissement-display-78"
                                value={selectedCommune ? selectedCommune.arrondissement : ""}
                                readOnly
                                disabled
                                aria-label={t('form.arrondissement.display')}
                                style={{
                                    backgroundColor: 'var(--background-disabled-grey)',
                                    cursor: 'not-allowed',
                                }}
                            />
                        </div>
                    </div>
                </div>
                {error && (
                    <p className="fr-error-text" id={`${inputId}-error`} role="alert" aria-live="assertive">
                        {error}
                    </p>
                )}
            </div>
        </div >
    );
}
