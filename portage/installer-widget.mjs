// Fort Énigma — ajoute le widget de l'écran d'accueil au projet Android
// généré par Capacitor (à lancer après « npx cap add android » et « npx cap sync android »).
// Copie widget-android/{java,res} dans android/app/src/main/ et déclare le
// récepteur du widget dans AndroidManifest.xml (sans doublon si relancé).
import { cpSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ici = dirname(fileURLToPath(import.meta.url));
const main = join(ici, "android", "app", "src", "main");
if (!existsSync(main)) { console.error("Projet Android absent : lancez d'abord npx cap add android."); process.exit(1); }
cpSync(join(ici, "widget-android", "java"), join(main, "java"), { recursive: true });
cpSync(join(ici, "widget-android", "res"), join(main, "res"), { recursive: true });

const manifeste = join(main, "AndroidManifest.xml");
let m = readFileSync(manifeste, "utf8");
if (!m.includes(".FortWidget")) {
  const recepteur = `
        <receiver android:name="app.netlify.fortenigma.FortWidget" android:exported="false" android:label="@string/fort_widget_nom">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
                <action android:name="android.intent.action.TIME_SET" />
                <action android:name="android.intent.action.TIMEZONE_CHANGED" />
            </intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/fort_widget_info" />
        </receiver>
`;
  if (!m.includes("</application>")) { console.error("AndroidManifest.xml inattendu"); process.exit(1); }
  m = m.replace("</application>", recepteur + "    </application>");
  writeFileSync(manifeste, m);
}
console.log("Widget Fort Énigma installé dans le projet Android.");
