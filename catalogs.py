CROPS={
"Cacao":{"kc":1.05,"zr":1.0,"p":.30,"plant":3.0,"row":3.0,"method":"Goteo/Microaspersión","ref":"FAO-56; marco editable según material y manejo"},
"Café":{"kc":.95,"zr":.9,"p":.40,"plant":1.5,"row":2.0,"method":"Goteo","ref":"FAO-56; marco editable"},
"Banano":{"kc":1.10,"zr":.7,"p":.35,"plant":2.5,"row":2.5,"method":"Goteo/Microaspersión","ref":"FAO-56; ajustar clon y sistema"},
"Caña de azúcar":{"kc":1.25,"zr":1.2,"p":.65,"plant":.5,"row":1.5,"method":"Goteo/Aspersión/Surcos","ref":"FAO-56; espaciamiento editable según sistema"},
"Aguacate":{"kc":.85,"zr":1.0,"p":.50,"plant":6.0,"row":6.0,"method":"Microaspersión/Goteo","ref":"Valor inicial editable; validar cultivar, edad y cobertura"},
"Cítricos":{"kc":.70,"zr":1.1,"p":.50,"plant":5.0,"row":6.0,"method":"Microaspersión/Goteo","ref":"FAO-56; ajustar cobertura y manejo"},
"Maíz":{"kc":1.20,"zr":1.0,"p":.55,"plant":.25,"row":.8,"method":"Aspersión/Goteo","ref":"FAO-56"},
"Papa":{"kc":1.15,"zr":.6,"p":.35,"plant":.30,"row":.9,"method":"Aspersión/Goteo","ref":"FAO-56"},
"Personalizado":{"kc":1.0,"zr":.6,"p":.50,"plant":1.0,"row":1.0,"method":"Personalizado","ref":"Usuario"}
}
MATERIALS={"PVC":150.0,"PEAD / HDPE":150.0,"PEBD":150.0,"Acero comercial":120.0,"Hierro dúctil":130.0}
METHODS=["Goteo","Microaspersión","Aspersión","Gravedad"]
REGIMES=["Permanente","Transitorio / intermitente","Efímero","Desconocido"]

METHOD_PROFILES={
"Goteo":{"eff":0.90,"pressure_mca":10.0,"emitter_lh":2.0,"wet_m":0.5,"wind":2.0,"dn_main":90,"dn_sec":63,"dn_lat":20,"note":"Inicial editable; sustituir presión/caudal por ficha técnica del gotero."},
"Microaspersión":{"eff":0.85,"pressure_mca":20.0,"emitter_lh":40.0,"wet_m":8.0,"wind":2.0,"dn_main":90,"dn_sec":63,"dn_lat":25,"note":"Inicial editable; usar ficha técnica del microaspersor."},
"Aspersión":{"eff":0.75,"pressure_mca":30.0,"emitter_lh":800.0,"wet_m":24.0,"wind":2.0,"dn_main":110,"dn_sec":75,"dn_lat":40,"note":"Inicial editable; espaciamiento depende de diámetro mojado, viento y uniformidad."},
"Gravedad":{"eff":0.60,"pressure_mca":0.0,"emitter_lh":0.0,"wet_m":0.0,"wind":0.0,"dn_main":110,"dn_sec":90,"dn_lat":50,"note":"Sin presión de emisor; verificar pendiente, infiltración y caudal."}
}
MATERIAL_INFO={
"PVC":{"C":150.0,"note":"C=150 inicial. Dint requiere clase/PN y catálogo."},
"PEAD / HDPE":{"C":150.0,"note":"C=150 inicial. Dint requiere SDR/PN y catálogo."},
"PEBD":{"C":150.0,"note":"C=150 inicial. Dint requiere SDR/PN y catálogo."},
"Acero comercial":{"C":120.0,"note":"C=120 inicial; condición/edad modifica rugosidad."},
"Hierro dúctil":{"C":130.0,"note":"C=130 inicial; verificar revestimiento y condición."}
}
