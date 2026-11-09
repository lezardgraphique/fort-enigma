# Fort Énigma — capture de l'accueil avec le VRAI moteur de Safari (WebKit, via WebKitGTK).
# Installation (Ubuntu) : sudo apt-get install xvfb python3-gi gir1.2-webkit2-4.1 gir1.2-gtk-3.0
# Usage : xvfb-run -a python3 outils/capture-webkit.py LARGEUR HAUTEUR HEURE MOIS(-1=actuel) sortie.png ["user-agent"] ["expression JS"] [attente_ms]
# Exemple iPad sous iOS 15 :
#   xvfb-run -a python3 outils/capture-webkit.py 1024 768 21 -1 ipad.png "Mozilla/5.0 (iPad; CPU OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1"
import sys, gi
gi.require_version('Gtk', '3.0'); gi.require_version('WebKit2', '4.1')
from gi.repository import Gtk, WebKit2, GLib
w, h, H, mo, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
ua = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] else None
js = sys.argv[7] if len(sys.argv) > 7 else None
attente = int(sys.argv[8]) if len(sys.argv) > 8 else 7000
clk = """(()=>{const R=Date;const off=(()=>{const d=new R();const t=new R(d);%st.setHours(%d,25,0,0);return t-d})();class F extends R{constructor(...a){if(a.length)super(...a);else super(R.now()+off)} static now(){return R.now()+off}};window.Date=F;})()""" % (("t.setMonth(%d,12);" % mo) if mo >= 0 else "", H)
ucm = WebKit2.UserContentManager()
ucm.add_script(WebKit2.UserScript(clk, WebKit2.UserContentInjectedFrames.TOP_FRAME, WebKit2.UserScriptInjectionTime.START, None, None))
ucm.add_script(WebKit2.UserScript("window.__wkErr=[];addEventListener('error',e=>__wkErr.push(String(e.message)+' @'+(e.lineno||'')));", WebKit2.UserContentInjectedFrames.TOP_FRAME, WebKit2.UserScriptInjectionTime.START, None, None))
v = WebKit2.WebView.new_with_user_content_manager(ucm)
s = v.get_settings(); s.set_allow_file_access_from_file_urls(True); s.set_allow_universal_access_from_file_urls(True); s.set_enable_write_console_messages_to_stdout(False)
if ua: s.set_user_agent(ua)
win = Gtk.Window(); win.set_default_size(w, h); win.add(v); win.show_all()
def fini(src, res):
  try:
    surf = v.get_snapshot_finish(res); surf.write_to_png(out)
  except Exception as e: print('snapshot KO', e)
  Gtk.main_quit()
def apres_js(src, res):
  try:
    r = v.evaluate_javascript_finish(res); print(r.to_string())
  except Exception as e: print('js KO', e)
  v.get_snapshot(WebKit2.SnapshotRegion.VISIBLE, WebKit2.SnapshotOptions.NONE, None, fini)
def go():
  code = "JSON.stringify({err:window.__wkErr, r:(function(){try{return (%s)}catch(e){return 'ERR '+e}})()})" % (js or "0")
  v.evaluate_javascript(code, -1, None, None, None, apres_js); return False
v.load_uri('file://' + __import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'index.html')) + '?meteo=0')
GLib.timeout_add(attente, go); GLib.timeout_add(attente + 20000, lambda: Gtk.main_quit())
Gtk.main()
