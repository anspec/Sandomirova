(function () {
  "use strict";

  document.documentElement.classList.add("js");

  const PLACEHOLDER_ICON =
    '<svg class="placeholder__icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
    '<rect x="6" y="10" width="36" height="28" rx="2" stroke="currentColor" stroke-width="2"/>' +
    '<circle cx="18" cy="22" r="4" stroke="currentColor" stroke-width="2"/>' +
    '<path d="M6 32l10-8 8 6 8-10 10 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' +
    "</svg>";

  var portfolioData = [
    { image: "photo/featured-works/abstract-stained-glass-facade.jpg", story: "photo/featured-works/abstract-stained-glass-facade.txt", title: "Abstract Stained Glass Facade", meta: "Избранные работы", alt: "Abstract Stained Glass Facade" },
    { image: "photo/featured-works/interior-monumental-solution.jpg", story: "photo/featured-works/interior-monumental-solution.txt", title: "Interior Monumental Solution", meta: "Избранные работы · частное пространство", alt: "Interior Monumental Solution" },
    { image: "photo/featured-works/mosaic-assembly-featured.jpg", story: "photo/featured-works/mosaic-assembly-featured.txt", title: "Mosaic Assembly", meta: "Избранные работы · мозаика", alt: "Mosaic Assembly" },
    { image: "photo/featured-works/author-glass-objects.jpg", story: "photo/featured-works/author-glass-objects.txt", title: "Author Glass Objects", meta: "Избранные работы · коллекция", alt: "Author Glass Objects" },
    { image: "photo/featured-works/expo-85-tsukuba-glass.jpg", story: "photo/featured-works/expo-85-tsukuba-glass.txt", title: "Expo 85, Tsukuba", meta: "Япония · 1985 · художественное стекло", alt: "Expo 85 Tsukuba Glass" },
    { image: "photo/featured-works/vitrazh-botanical-ornament.jpg", story: "photo/featured-works/vitrazh-botanical-ornament.txt", title: "Vitrazh Botanical Ornament", meta: "Избранные работы · витраж", alt: "Vitrazh Botanical Ornament" },
    { image: "photo/featured-works/urban-serenity-stained-glass.jpg", story: "photo/featured-works/urban-serenity-stained-glass.txt", title: "Urban Serenity Stained Glass", meta: "Избранные работы · витраж", alt: "Urban Serenity Stained Glass" },
    { image: "photo/featured-works/glass-stone-sculpture-featured.jpg", story: "photo/featured-works/glass-stone-sculpture-featured.txt", title: "Glass and Stone Sculpture", meta: "Избранные работы · авторский объект", alt: "Glass Stone Sculpture" },
    { image: "photo/featured-works/amber-light-panels-featured.jpg", story: "photo/featured-works/amber-light-panels-featured.txt", title: "Amber Light Panels", meta: "Избранные работы · свет", alt: "Amber Light Panels" },
    { image: "photo/featured-works/mural-portrait-featured.jpg", story: "photo/featured-works/mural-portrait-featured.txt", title: "Mural Portrait", meta: "Избранные работы · роспись", alt: "Mural Portrait" },
    { image: "photo/featured-works/vitrazh-birds-composition.jpg", story: "photo/featured-works/vitrazh-birds-composition.txt", title: "Vitrazh Birds Composition", meta: "Избранные работы · витраж", alt: "Vitrazh Birds Composition" },
  ];

  function init() {
    document.querySelectorAll("[data-placeholder]").forEach(function (el) {
      var label = el.getAttribute("data-placeholder");
      el.innerHTML = PLACEHOLDER_ICON + '<span class="placeholder__label">' + label + "</span>";
    });

    var modal = document.getElementById("portfolioModal");
    var modalClose = document.getElementById("modalClose");
    var modalImageWrap = document.getElementById("modalImageWrap");
    var modalTitle = document.getElementById("modalTitle");
    var modalMeta = document.getElementById("modalMeta");
    var modalStory = document.getElementById("modalStory");

    function setStoryHtml(html) {
      if (modalStory) modalStory.innerHTML = html;
    }

    function parseStory(text) {
      var fields = [];
      text.split(/\r?\n/).forEach(function (line) {
        var idx = line.indexOf(":");
        if (idx === -1) return;
        var key = line.slice(0, idx).trim();
        var value = line.slice(idx + 1).trim();
        if (!key || key === "Примечание") return;
        fields.push({ key: key, value: value });
      });
      return fields;
    }

    function renderStory(fields) {
      if (!fields.length) {
        setStoryHtml("<p>Описание проекта будет добавлено.</p>");
        return;
      }
      setStoryHtml(
        '<dl class="modal__details">' +
        fields.map(function (f) {
          return "<dt>" + f.key + "</dt><dd>" + f.value + "</dd>";
        }).join("") +
        "</dl>"
      );
    }

    function loadStory(url) {
      setStoryHtml('<p class="modal__loading">Загрузка описания…</p>');
      fetch(url)
        .then(function (r) {
          if (!r.ok) throw new Error("not found");
          return r.text();
        })
        .then(function (text) {
          renderStory(parseStory(text));
        })
        .catch(function () {
          setStoryHtml("<p>Описание проекта будет добавлено.</p>");
        });
    }

    function openModal(index) {
      var item = portfolioData[index];
      if (!item || !modal || !modalTitle || !modalMeta || !modalImageWrap) return;

      modalTitle.textContent = item.title;
      modalMeta.textContent = item.meta;
      modalImageWrap.innerHTML =
        '<img class="modal__img" src="' + item.image + '" alt="' + (item.alt || item.title) + '">';

      if (item.story) loadStory(item.story);
      else setStoryHtml("");

      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }

    function closeModal() {
      if (!modal) return;
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }

    var grid = document.getElementById("portfolioGrid");
    if (grid) {
      grid.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-portfolio]");
        if (!btn || !grid.contains(btn)) return;
        openModal(parseInt(btn.getAttribute("data-portfolio"), 10));
      });
    }

    if (modalClose) modalClose.addEventListener("click", closeModal);
    if (modal) {
      modal.addEventListener("click", function (e) {
        if (e.target === modal) closeModal();
      });
    }
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal && modal.classList.contains("open")) closeModal();
    });

    var menuToggle = document.getElementById("menuToggle");
    var nav = document.getElementById("nav");
    if (menuToggle && nav) {
      menuToggle.addEventListener("click", function () {
        var open = nav.classList.toggle("open");
        menuToggle.setAttribute("aria-expanded", open);
      });
      nav.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
          nav.classList.remove("open");
          menuToggle.setAttribute("aria-expanded", "false");
        });
      });
    }

    var fadeEls = document.querySelectorAll(".fade-in");
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
      );
      fadeEls.forEach(function (el) {
        observer.observe(el);
      });
    } else {
      fadeEls.forEach(function (el) {
        el.classList.add("visible");
      });
    }

    var contactForm = document.getElementById("contactForm");
    if (contactForm) {
      contactForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var form = e.target;
        if (!form.checkValidity()) {
          form.reportValidity();
          return;
        }
        var formSuccess = document.getElementById("formSuccess");
        if (formSuccess) formSuccess.classList.add("visible");
        form.reset();
        var submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
      });
    }

    var heroFade = document.querySelector(".hero .fade-in");
    if (heroFade) heroFade.classList.add("visible");
  }

  try {
    init();
  } catch (err) {
    document.querySelectorAll(".fade-in").forEach(function (el) {
      el.classList.add("visible");
    });
    if (window.console && console.error) console.error(err);
  }
})();
