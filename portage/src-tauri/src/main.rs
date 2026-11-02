// Fort Énigma sur PC : une fenêtre qui affiche le jeu embarqué (dossier www/).
// Pas de console sous Windows en version finale.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("le Fort n'a pas pu s'ouvrir");
}
