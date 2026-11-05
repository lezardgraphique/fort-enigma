package app.netlify.fortenigma;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;
import java.util.Calendar;

/**
 * Fort Énigma — widget de l'écran d'accueil.
 * Affiche si le Fort est ouvert ou fermé, le passage d'effraction de la nuit
 * (le même que dans le jeu) et la Foire secrète la nuit. Tout est calculé sur
 * le téléphone, sans réseau. Un appui ouvre le jeu.
 */
public class FortWidget extends AppWidgetProvider {
    static final String MAJ = "app.netlify.fortenigma.FORT_WIDGET_MAJ";

    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, vue(ctx));
        programmer(ctx);
    }

    @Override
    public void onReceive(Context ctx, Intent intent) {
        super.onReceive(ctx, intent);
        String a = intent.getAction();
        if (MAJ.equals(a) || Intent.ACTION_TIME_CHANGED.equals(a) || Intent.ACTION_TIMEZONE_CHANGED.equals(a)) {
            AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
            onUpdate(ctx, mgr, mgr.getAppWidgetIds(new ComponentName(ctx, FortWidget.class)));
        }
    }

    @Override
    public void onDisabled(Context ctx) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(alarme(ctx));
    }

    static RemoteViews vue(Context ctx) {
        Calendar now = Calendar.getInstance();
        boolean nuit = FortSoir.ferme(now);
        int p = FortSoir.passageAnnonce(now);
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.fort_widget);
        v.setInt(R.id.fw_racine, "setBackgroundResource", nuit ? R.drawable.fort_widget_fond_nuit : R.drawable.fort_widget_fond_jour);
        v.setTextViewText(R.id.fw_etat, nuit ? "🌙 Le Fort est fermé" : "☀️ Le Fort est ouvert");
        v.setTextViewText(R.id.fw_passage, (nuit ? "Cette nuit, on entre par " : "Ce soir, on entrera par ")
            + FortSoir.COURT[p] + " " + FortSoir.ICONE[p]);
        v.setTextViewText(R.id.fw_foire, nuit
            ? "🎪 Derrière les remparts, la Foire secrète est ouverte"
            : "Le Fort ferme ses portes à 18 h");
        v.setTextViewText(R.id.fw_jouer, nuit ? "Tenter l’effraction ▸" : "Jouer ▸");
        Intent lancer = ctx.getPackageManager().getLaunchIntentForPackage(ctx.getPackageName());
        if (lancer != null) {
            lancer.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            PendingIntent pi = PendingIntent.getActivity(ctx, 0, lancer, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            v.setOnClickPendingIntent(R.id.fw_racine, pi);
            v.setOnClickPendingIntent(R.id.fw_jouer, pi);
        }
        return v;
    }

    static PendingIntent alarme(Context ctx) {
        Intent i = new Intent(ctx, FortWidget.class).setAction(MAJ);
        return PendingIntent.getBroadcast(ctx, 1, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    /** Réveil (inexact, sans permission particulière) à 6 h ou 18 h pour basculer jour / nuit. */
    static void programmer(Context ctx) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        am.setAndAllowWhileIdle(AlarmManager.RTC, FortSoir.prochainChangement(Calendar.getInstance()), alarme(ctx));
    }
}
