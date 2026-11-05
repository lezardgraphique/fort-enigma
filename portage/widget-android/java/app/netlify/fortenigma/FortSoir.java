package app.netlify.fortenigma;

import java.util.Calendar;

/**
 * Fort Énigma — calendrier du Fort, pour le widget.
 * Même calcul que la couche fort-effraction du jeu : le passage d'une nuit est
 * tiré à partir de la date du soir qui l'a commencée, jamais deux soirs de suite
 * le même. (Le jeu remplace aussi la poterne par le souterrain les soirs
 * d'orage ; le widget ne connaît pas la météo du jeu et ne le fait pas.)
 */
public final class FortSoir {
    private FortSoir() {}

    public static final String[] ORDRE = {"grilles", "poterne", "rempart", "charrette", "souterrain"};
    public static final String[] COURT = {
        "les grilles du Contrebandier", "la poterne de la mer", "l’échelle du rempart",
        "la charrette du Contrebandier", "le souterrain oublié"};
    public static final String[] ICONE = {"🔒", "🌊", "🪜", "🛒", "🕯️"};

    /** Le Fort ferme de 18 h à 6 h (phases soir et nuit du jeu). */
    public static boolean ferme(Calendar c) {
        int h = c.get(Calendar.HOUR_OF_DAY);
        return h >= 18 || h < 6;
    }

    static int cle(Calendar c) {
        return c.get(Calendar.YEAR) * 10000 + (c.get(Calendar.MONTH) + 1) * 100 + c.get(Calendar.DAY_OF_MONTH);
    }

    static long hache(int n) {
        n = (n ^ 61) ^ (n >>> 16);
        n = n + (n << 3);
        n ^= n >>> 4;
        n = n * 0x27d4eb2d;
        n ^= n >>> 15;
        return n & 0xffffffffL;
    }

    static int tirage(Calendar soir) { return (int) (hache(cle(soir)) % ORDRE.length); }

    /** Indice du passage pour la nuit qui commence le soir du jour donné. */
    public static int passagePourLeSoirDu(Calendar jour) {
        Calendar s = (Calendar) jour.clone();
        int m = tirage(s);
        Calendar veille = (Calendar) jour.clone();
        veille.add(Calendar.DAY_OF_MONTH, -1);
        if (m == tirage(veille)) m = (m + 1) % ORDRE.length;
        return m;
    }

    /**
     * Le passage à annoncer maintenant : la nuit en cours (avant midi, elle appartient
     * au soir de la veille), ou celle de ce soir pendant la journée.
     */
    public static int passageAnnonce(Calendar maintenant) {
        Calendar j = (Calendar) maintenant.clone();
        if (maintenant.get(Calendar.HOUR_OF_DAY) < 6) j.add(Calendar.DAY_OF_MONTH, -1);
        return passagePourLeSoirDu(j);
    }

    /** Prochain changement d'affichage : 6 h ou 18 h. */
    public static long prochainChangement(Calendar maintenant) {
        Calendar p = (Calendar) maintenant.clone();
        p.set(Calendar.MINUTE, 0); p.set(Calendar.SECOND, 5); p.set(Calendar.MILLISECOND, 0);
        int h = maintenant.get(Calendar.HOUR_OF_DAY);
        if (h < 6) p.set(Calendar.HOUR_OF_DAY, 6);
        else if (h < 18) p.set(Calendar.HOUR_OF_DAY, 18);
        else { p.add(Calendar.DAY_OF_MONTH, 1); p.set(Calendar.HOUR_OF_DAY, 6); }
        return p.getTimeInMillis();
    }
}
