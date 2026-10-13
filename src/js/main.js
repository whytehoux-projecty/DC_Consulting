/* DC Consulting — site scripts. No dependencies.
   Settings (form URL, enquiry email) come from js/config.js, written by the build. */
var DC_CONFIG = window.DC_CONFIG || { formEndpoint: "", enquiryEmail: "enquiries@example.com" };

(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  var btn = document.getElementById("menu-btn");
  var drawer = document.getElementById("mobile-nav");
  if (btn && drawer) {
    var setOpen = function (open) {
      drawer.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };
    btn.addEventListener("click", function () {
      setOpen(!drawer.classList.contains("open"));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer.classList.contains("open")) {
        setOpen(false);
        btn.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth >= 980) setOpen(false);
    });
  }

  /* ---------- Enquiry form ---------- */
  var form = document.getElementById("enquiry-form");
  if (!form) return;

  // Incoterms are used correctly: sea-only terms (FOB, CFR, CIF) for ship cargo,
  // multimodal terms (FCA, CIP, DAP, DDP) for containers, air and vault delivery.
  var CONFIG = {
    "Rare earths & critical minerals": {
      label: "Material",
      items: [
        "NdPr oxide or metal",
        "Dysprosium / terbium oxides",
        "Tantalum / niobium concentrate",
        "Tungsten concentrate (wolframite / scheelite)",
        "Titanium feedstock (rutile / ilmenite)",
        "Lithium or cobalt intermediates",
        "Mixed rare earth carbonate (MREC)",
        "Other (describe in notes)"
      ],
      units: ["Metric tonnes", "Kilograms", "20ft containers"],
      terms: ["FOB (sea)", "CFR (sea)", "CIF (sea)", "FCA (any mode)", "CIP (any mode)", "DAP (any mode)", "Not sure — advise me"]
    },
    "Crude oil & petroleum products": {
      label: "Grade or product",
      items: [
        "Light sweet crude",
        "Medium or heavy crude",
        "Condensate",
        "Diesel (e.g. EN 590)",
        "Jet A-1",
        "Fuel oil",
        "Other (describe in notes)"
      ],
      units: ["Barrels", "Metric tonnes", "Cubic metres"],
      terms: ["FOB (loading terminal)", "CFR (discharge port)", "CIF (discharge port)", "DAP (delivered at place)", "Not sure — advise me"]
    },
    "Gemstones": {
      label: "Stone type and form",
      items: [
        "Rough diamonds",
        "Polished diamonds",
        "Emerald, ruby or sapphire (rough or cut)",
        "Other coloured stones (tourmaline, aquamarine, garnet…)",
        "Industrial or optical crystals",
        "Other (describe in notes)"
      ],
      units: ["Carats", "Grams", "Kilograms"],
      terms: ["FCA (any mode)", "CIP (any mode)", "DAP (any mode)", "Not sure — advise me"]
    },
    "Other materials": {
      label: "Material",
      items: [
        "Copper cathode",
        "Gold doré",
        "Platinum group metals",
        "Manganese, chrome or bauxite",
        "Other (describe in notes)"
      ],
      units: ["Metric tonnes", "Kilograms", "Troy ounces", "Other (state in notes)"],
      terms: ["FOB (sea)", "CFR (sea)", "CIF (sea)", "FCA (any mode)", "CIP (any mode)", "DAP (any mode)", "Not sure — advise me"]
    }
  };

  var $ = function (id) { return document.getElementById(id); };
  var division = $("f-division");
  var item = $("f-item");
  var itemLabel = $("f-item-label");
  var unit = $("f-unit");
  var terms = $("f-terms");
  var status = $("form-status");

  function fill(select, values) {
    select.textContent = "";
    values.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v;
      o.textContent = v;
      select.appendChild(o);
    });
  }

  function updateFields() {
    var c = CONFIG[division.value] || CONFIG["Rare earths & critical minerals"];
    itemLabel.textContent = c.label;
    fill(item, c.items);
    fill(unit, c.units);
    fill(terms, c.terms);
  }

  // Pre-select a division from ?division=... (used by "Start an enquiry" links)
  var params = new URLSearchParams(window.location.search);
  var pre = params.get("division");
  if (pre && CONFIG[pre]) division.value = pre;
  updateFields();
  division.addEventListener("change", updateFields);

  function show(kind, message) {
    status.className = "form-status show " + kind;
    status.textContent = message; // textContent only: user input is never parsed as HTML
    status.setAttribute("tabindex", "-1");
    status.focus();
  }

  function val(id) { return ($(id).value || "").trim(); }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Honeypot: real people never see or fill this field
    if (val("f-website")) return;

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    var payload = {
      organisation: val("f-org"),
      role: val("f-role"),
      name: val("f-name"),
      email: val("f-email"),
      phone: val("f-phone"),
      division: division.value,
      material: item.value,
      volume: val("f-volume") + " " + unit.value,
      delivery_terms: terms.value,
      destination: val("f-dest"),
      timing: val("f-timing"),
      services: Array.prototype.map.call(
        form.querySelectorAll('input[name="services"]:checked'),
        function (cb) { return cb.value; }
      ).join(", ") || "Not specified",
      notes: val("f-notes") || "None",
      confidentiality_agreement_requested: $("f-nda").checked ? "Yes" : "No"
    };

    if (DC_CONFIG.formEndpoint) {
      var submitBtn = form.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      fetch(DC_CONFIG.formEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload)
      }).then(function (r) {
        if (!r.ok) throw new Error("bad status");
        form.reset();
        updateFields();
        show("ok", "Thank you. Your enquiry has been received and we will reply to the email address you provided.");
      }).catch(function () {
        show("err", "We could not send your enquiry. Please email " + DC_CONFIG.enquiryEmail + " directly.");
      }).then(function () { submitBtn.disabled = false; });
      return;
    }

    // Fallback with no backend: open the visitor's email app with the details filled in.
    var lines = Object.keys(payload).map(function (k) {
      return k.replace(/_/g, " ") + ": " + payload[k];
    });
    var subject = "Enquiry: " + payload.division + " — " + payload.organisation;
    var href = "mailto:" + DC_CONFIG.enquiryEmail +
      "?subject=" + encodeURIComponent(subject) +
      "&body=" + encodeURIComponent(lines.join("\n"));
    window.location.href = href;
    show("ok", "Your email app should now open with your enquiry filled in. Nothing has been sent until you press Send there. If it did not open, email " + DC_CONFIG.enquiryEmail + " directly.");
  });
})();
