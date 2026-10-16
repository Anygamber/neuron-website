/**
 * NeurON site i18n — RU / O'Z / EN
 * Approach: single page + translation dictionary (data-i18n attributes).
 * Language: ?lang=uz|ru|en + localStorage.neuron_lang (default: uz)
 * SEO overrides: i18n-seo.js → NEURON_I18N_EXTRA
 */
(function () {
  const STORAGE_KEY = "neuron_lang";
  const SUPPORTED = ["ru", "uz", "en"];

  const META = {
    ru: {
      title: "Нейрохирург Ташкент | NeurON — нейрохирургия и Центр боли",
      description: "Нейрохирург в Ташкенте: опухоль головного мозга, аневризма, грыжа позвоночника, невралгия тройничного нерва, эпилепсия, лечение боли (блокады, РЧА, COSMAN G4). Клиника NeurON.",
      keywords: "нейрохирург Ташкент, нейрохирургия, опухоль головного мозга, менингиома, глиома, аневризма головного мозга, АВМ, грыжа позвоночника, микродискэктомия, невралгия тройничного нерва, Центр боли, эпидуральная блокада, РЧА, COSMAN G4, хирургия эпилепсии",
      ogLocale: "ru_RU",
      ogUrl: "https://neuronmedical.uz/?lang=ru"
    },
    uz: {
      title: "Neyroxirurg Toshkent | NeurON — neyroxirurgiya va Og‘riq markazi",
      description: "Toshkentda neyroxirurg: miya o‘smasi, anevrizma, umurtqa churrasi, uch shoxli nerv nevralgiyasi, epilepsiya, og‘riqni davolash (blokada, RChA, COSMAN G4). NeurON klinikasi.",
      keywords: "neyroxirurg Toshkent, neyroxirurgiya, miya o‘smasi, meningioma, glioma, miya anevrizmasi, AVM, umurtqa churrasi, mikrodisketomiya, uch shoxli nerv nevralgiyasi, og‘riq markazi, epidural blokada, RChA, COSMAN G4, epilepsiya jarrohligi",
      ogLocale: "uz_UZ",
      ogUrl: "https://neuronmedical.uz/?lang=uz"
    },
    en: {
      title: "Neurosurgeon Tashkent | NeurON — Neurosurgery & Pain Management",
      description: "Neurosurgeon in Tashkent, Uzbekistan: brain tumor, aneurysm, disc herniation, trigeminal neuralgia, epilepsy surgery, Pain Management (epidural block, RFA, COSMAN G4). NeurON Medical Centre.",
      keywords: "neurosurgeon Tashkent, neurosurgery Uzbekistan, brain tumor, meningioma, glioma, cerebral aneurysm, AVM, disc herniation, microdiscectomy, trigeminal neuralgia, Pain Management, epidural block, RFA, COSMAN G4, epilepsy surgery",
      ogLocale: "en_US",
      ogUrl: "https://neuronmedical.uz/?lang=en"
    }
  };

  const DICT = {
    ru: {
      "nav.services": "Услуги",
      "nav.prices": "Прейскурант",
      "nav.doctors": "Врачи",
      "nav.about": "О клинике",
      "nav.tech": "Технологии",
      "nav.contacts": "Контакты",
      "nav.aria": "Основная навигация",
      "nav.mobileAria": "Мобильное меню",
      "a11y.skip": "Перейти к услугам",
      "social.instagram": "Instagram",
      "social.instagramAria": "NeurON в Instagram — @neuronmed.uz",
      "social.followTitle": "Мы в социальных сетях",
      "social.telegram": "Telegram",
      "social.facebook": "Facebook",
      "social.whatsapp": "WhatsApp",
      "social.telegramAria": "NeurON в Telegram — @neuronmedical_center",
      "social.facebookAria": "NeurON в Facebook",
      "social.whatsappAria": "Написать в WhatsApp — +998 71 200-00-20",
      "lang.ruTitle": "Русский",
      "lang.uzTitle": "O‘zbek tili",
      "lang.enTitle": "English",
      "footer.legalEntity": "ООО «NeurON Medical Centre»",
      "header.search": "Поиск",
      "header.searchAria": "Открыть поиск по сайту",
      "header.contacts": "Контакты",
      "header.phoneAria": "Позвонить в клинику",
      "header.burgerAria": "Открыть меню",
      "header.brandAria": "NeurON Medical Centre — на главную",
      "prices.catalogIdle": "В каталоге: <strong>{n}</strong> услуг · выберите категорию или поиск",
      "prices.idleTitle": "Прейскурант готов к просмотру",
      "prices.idleText": "Выберите категорию выше или введите название услуги в поиск, чтобы увидеть прейскурант",
      "prices.showAll": "Показать все услуги",
      "prices.openSearch": "Открыть поиск",
      "prices.currency": "Валюта: узбекский сум · г. Ташкент",
      "prices.all": "Все",
      "prices.allTitle": "Все категории",
      "prices.colService": "Услуга",
      "prices.colCost": "Стоимость",
      "prices.servicesN": "услуг",
      "prices.found": "Найдено: <strong>{n}</strong> из {total} услуг",
      "prices.emptyTitle": "Ничего не найдено",
      "prices.emptyText": "Попробуйте другое название или категорию. Если нужной услуги нет в списке — свяжитесь с клиникой, мы подскажем и поможем с записью.",
      "prices.reset": "Сбросить поиск",
      "prices.filtersAria": "Категории услуг",
      "prices.searchPh": "Живой поиск: МРТ, анализы, нейрохирургия, блокада…",
      "prices.searchAria": "Живой поиск по прейскуранту",
      "prices.clearAria": "Очистить поиск",
      "prices.legal": "Цены носят информационный характер и могут изменяться. Имеются противопоказания — необходима консультация специалиста. Итоговая стоимость подтверждается администратором при записи.",
      "prices.loading": "Загрузка прейскуранта…",
      "mobile.search": "Поиск по сайту",
      "hero.title": "Точная нейрохирургия и инновационные технологии для вашего <span>здоровья</span>",
      "hero.lead": "Высокоспециализированная многопрофильная клиника: нейрохирургия, диагностика экспертного уровня и малоинвазивные вмешательства.",
      "hero.ctaServices": "Смотреть направления",
      "trust.1.title": "Лицензированная клиника",
      "trust.1.text": "Разрешительная документация и соответствие медицинским стандартам",
      "trust.2.title": "Частный медицинский центр",
      "trust.2.text": "Высокоспециализированная многопрофильная частная клиника",
      "trust.3.title": "Доказательная база",
      "trust.3.text": "МСКТ-контроль оперированных пациентов для подтверждения качества",
      "trust.4.title": "Полный цикл помощи",
      "trust.4.text": "Диагностика → хирургия → реанимация → восстановление",
      "services.label": "01 · Услуги",
      "services.title": "Направления нейрохирургии и хирургии",
      "services.lead": "Интерактивные направления с акцентом на безопасность, малоинвазивность и передовые технологии. Цены — ориентировочные диапазоны, точная стоимость после консультации.",
      "services.ctaTitle": "Нужна консультация по направлению?",
      "services.ctaText": "Позвоните в клинику или напишите на email — поможем выбрать специалиста.",
      "svc.neuro.title": "Нейрохирургия",
      "svc.neuro.price": "от 8 500 000 сум",
      "svc.neuro.body": "Полный спектр нейрохирургической помощи: опухоли головного мозга, травмы, сосудистые патологии, заболевания позвоночника и спинного мозга. Эндоскопические операции на позвоночнике — приоритетное направление.",
      "svc.neuro.li1": "Опухоли головного мозга и позвоночника",
      "svc.neuro.li2": "Эндоскопическая хирургия позвоночника",
      "svc.neuro.li3": "Сосудистые заболевания ЦНС",
      "svc.neuro.li4": "Дегенеративные поражения позвоночника",
      "svc.neuro.metaTitle": "Безопасность",
      "svc.neuro.metaText": "Планирование с учётом функционального МРТ-сканирования проводящих путей. Послеоперационный МСКТ-контроль качества.",
      "svc.neuro.range": "<strong>Диапазон:</strong> консультация от 350 000 · операции от 8 500 000 сум",
      "svc.diag.title": "Диагностика экспертного уровня",
      "svc.diag.price": "от 450 000 сум",
      "svc.diag.body": "Диагностический отдел обеспечивает первичную и специализированную диагностику: МРТ с функциональным сканированием мозга, МСКТ, УЗИ, гастро-колоноскопия, лаборатория и комплексные программы чек-апа.",
      "svc.diag.li1": "МРТ с функциональным сканированием",
      "svc.diag.li2": "Спиральная КТ (МСКТ)",
      "svc.diag.li3": "УЗИ и эндоскопическая диагностика",
      "svc.diag.li4": "Чек-ап на тканевом уровне",
      "svc.diag.metaTitle": "Технологии",
      "svc.diag.metaText": "Функциональное МРТ выявляет целостность проводящих путей — данные, недоступные на обычном аппарате, критичны для планирования нейрохирургии.",
      "svc.diag.range": "<strong>Диапазон:</strong> от 450 000 до 4 500 000 сум",
      "svc.angio.title": "Ангиография и эндоваскулярные вмешательства",
      "svc.angio.price": "от 6 000 000 сум",
      "svc.angio.body": "Внутрисосудистые вмешательства без открытых операций: коронарография, стенты, баллонная пластика сосудов, эмболизация питающих сосудов опухоли и химиотерапия.",
      "svc.angio.li1": "Коронарография и стентирование",
      "svc.angio.li2": "Баллонная пластика сосудов нижних конечностей",
      "svc.angio.li3": "Эмболизация маточных артерий",
      "svc.angio.li4": "Закрытие сосудов опухоли",
      "svc.angio.metaTitle": "Малоинвазивность",
      "svc.angio.metaText": "В ряде случаев опухолевый процесс можно контролировать перекрытием питающего сосуда — без открытой операции.",
      "svc.angio.range": "<strong>Диапазон:</strong> от 6 000 000 сум",
      "svc.surg.title": "Сосудистая, общая и онкохирургия",
      "svc.surg.price": "от 5 500 000 сум",
      "svc.surg.body": "Хирургическое подразделение на 40 койках: сосудистая хирургия с лазером, общая хирургия, онкология, колопроктология, лапароскопическая онкохирургия органов брюшной полости и малого таза.",
      "svc.surg.li1": "Лазерная сосудистая хирургия",
      "svc.surg.li2": "Лапароскопическая онкохирургия",
      "svc.surg.li3": "Бариатрические операции",
      "svc.surg.li4": "Колопроктология",
      "svc.surg.metaTitle": "Инфраструктура",
      "svc.surg.metaText": "5 операционных залов с новейшим оборудованием и 2 операционных блока.",
      "svc.surg.range": "<strong>Диапазон:</strong> от 5 500 000 сум",
      "svc.plastic.title": "Пластическая хирургия",
      "svc.plastic.price": "от 7 000 000 сум",
      "svc.plastic.body": "Пластические вмешательства с применением специального лазера для максимального качества результата и контролируемой травматизации тканей.",
      "svc.plastic.li1": "Лазерные пластические методики",
      "svc.plastic.li2": "Эстетическая и реконструктивная хирургия",
      "svc.plastic.li3": "Индивидуальное планирование результата",
      "svc.plastic.metaTitle": "Качество",
      "svc.plastic.metaText": "Лазерные технологии повышают точность и эстетический исход вмешательства.",
      "svc.plastic.range": "<strong>Диапазон:</strong> от 7 000 000 сум",
      "svc.checkF.title": "Женский чек-ап «Гармония здоровья и красоты»",
      "svc.checkF.price": "2 600 000 сум",
      "svc.checkF.body": "Полная лабораторная диагностика ключевых систем организма (33 важнейших показателя). Разработано с учётом особенностей женского организма.",
      "svc.checkF.g1": "Гормональный статус",
      "svc.checkF.g1.li1": "Эстрадиол",
      "svc.checkF.g1.li2": "Пролактин",
      "svc.checkF.g1.li3": "Тестостерон общий",
      "svc.checkF.g1.li4": "ТТГ (тиреотропный гормон)",
      "svc.checkF.g1.li5": "Т4 свободный",
      "svc.checkF.g1.li6": "Антитела к ТПО (Анти-ТПО)",
      "svc.checkF.g1.li7": "Кортизол",
      "svc.checkF.g2": "Обмен веществ и витамины",
      "svc.checkF.g2.li1": "Витамин D (25-OH)",
      "svc.checkF.g2.li2": "Ферритин",
      "svc.checkF.g2.li3": "Железо сывороточное",
      "svc.checkF.g2.li4": "Глюкоза крови",
      "svc.checkF.g2.li5": "Инсулин",
      "svc.checkF.g2.li6": "Общий белок",
      "svc.checkF.g3": "Сердечно-сосудистая система и липидный профиль",
      "svc.checkF.g3.li1": "Холестерин общий",
      "svc.checkF.g3.li2": "ЛПНП (липопротеины низкой плотности)",
      "svc.checkF.g3.li3": "ЛПВП (липопротеины высокой плотности)",
      "svc.checkF.g3.li4": "Триглицериды",
      "svc.checkF.g3.li5": "Коэффициент атерогенности",
      "svc.checkF.g4": "Почки",
      "svc.checkF.g4.li1": "Креатинин",
      "svc.checkF.g4.li2": "Мочевина",
      "svc.checkF.g4.li3": "Мочевая кислота",
      "svc.checkF.g5": "Печень",
      "svc.checkF.g5.li1": "АЛТ",
      "svc.checkF.g5.li2": "АСТ",
      "svc.checkF.g5.li3": "Билирубин общий",
      "svc.checkF.g5.li4": "ГГТ",
      "svc.checkF.g6": "Воспаление и общее обследование",
      "svc.checkF.g6.li1": "СРБ (C-реактивный белок)",
      "svc.checkF.g6.li2": "Общий анализ крови (ОАК)",
      "svc.checkF.g6.li3": "Общий анализ мочи (ОАМ)",
      "svc.checkF.g6.li4": "СОЭ",
      "svc.checkF.g6.li5": "Гликированный гемоглобин (HbA1c)",
      "svc.checkF.g6.li6": "Кальций / магний (базовый минеральный профиль)",
      "svc.checkF.g6.li7": "Коагулограмма (базовые показатели свёртывания)",
      "svc.checkF.g6.li8": "Щелочная фосфатаза",
      "svc.checkF.metaTitle": "33 показателя",
      "svc.checkF.metaText": "Комплекс учитывает гормональный фон, обмен веществ, сосудистые риски, функцию почек и печени — для раннего выявления дисбалансов и поддержки женского здоровья.",
      "svc.checkF.range": "<strong>Стоимость:</strong> 2 600 000 сум",
      "svc.checkM.title": "Мужской чек-ап «Ключ к здоровью и долголетию»",
      "svc.checkM.price": "2 900 000 сум",
      "svc.checkM.body": "Полная лабораторная диагностика организма из 36 важнейших показателей — акцент на сосудистые риски, обмен веществ, мужское здоровье и долголетие.",
      "svc.checkM.g1": "Липидный профиль и сосудистые риски",
      "svc.checkM.g1.li1": "Холестерин общий",
      "svc.checkM.g1.li2": "ЛПНП",
      "svc.checkM.g1.li3": "ЛПВП",
      "svc.checkM.g1.li4": "Триглицериды",
      "svc.checkM.g1.li5": "Коэффициент атерогенности",
      "svc.checkM.g1.li6": "Гомоцистеин (при наличии в панели)",
      "svc.checkM.g2": "Углеводный обмен",
      "svc.checkM.g2.li1": "Глюкоза крови",
      "svc.checkM.g2.li2": "Гликированный гемоглобин (HbA1c)",
      "svc.checkM.g2.li3": "Инсулин",
      "svc.checkM.g2.li4": "Индекс HOMA-IR (расчётный)",
      "svc.checkM.g3": "Почки и мочевыделительная система",
      "svc.checkM.g3.li1": "Креатинин",
      "svc.checkM.g3.li2": "Мочевина",
      "svc.checkM.g3.li3": "Мочевая кислота",
      "svc.checkM.g3.li4": "Общий анализ мочи (ОАМ)",
      "svc.checkM.g4": "Печень и ЖКТ",
      "svc.checkM.g4.li1": "АЛТ",
      "svc.checkM.g4.li2": "АСТ",
      "svc.checkM.g4.li3": "Билирубин общий",
      "svc.checkM.g4.li4": "ГГТ",
      "svc.checkM.g4.li5": "CEA (раковый эмбриональный антиген)",
      "svc.checkM.g5": "Гормональный статус и мужское здоровье",
      "svc.checkM.g5.li1": "Тестостерон общий",
      "svc.checkM.g5.li2": "Пролактин",
      "svc.checkM.g5.li3": "ТТГ",
      "svc.checkM.g5.li4": "Т4 свободный",
      "svc.checkM.g5.li5": "ПСА общий (маркер предстательной железы)",
      "svc.checkM.g5.li6": "Кортизол",
      "svc.checkM.g6": "Витамины, железо и воспаление",
      "svc.checkM.g6.li1": "Витамин D (25-OH)",
      "svc.checkM.g6.li2": "Ферритин",
      "svc.checkM.g6.li3": "Железо сывороточное",
      "svc.checkM.g6.li4": "СРБ (C-реактивный белок)",
      "svc.checkM.g6.li5": "Общий анализ крови (ОАК)",
      "svc.checkM.g6.li6": "СОЭ",
      "svc.checkM.g6.li7": "Общий белок",
      "svc.checkM.g6.li8": "Щелочная фосфатаза",
      "svc.checkM.g6.li9": "Коагулограмма (базовые показатели)",
      "svc.checkM.g6.li10": "Магний / кальций (минеральный профиль)",
      "svc.checkM.g6.li11": "Антитела к ТПО (при показаниях в панели)",
      "svc.checkM.metaTitle": "36 показателей",
      "svc.checkM.metaText": "Программа помогает оценить сосудистые и метаболические риски, гормональный баланс и ресурс долголетия — с акцентом на мужское здоровье.",
      "svc.checkM.range": "<strong>Стоимость:</strong> 2 900 000 сум",
      "svc.pain.title": "Центр боли",
      "svc.pain.price": "Блокады · РЧА · COSMAN G4",
      "svc.pain.body": "Современное лечение хронической и острой боли без открытых хирургических вмешательств: лечебно-диагностические блокады и радиочастотная абляция (РЧА) на оборудовании COSMAN G4. Комплексный подход нейрохирургов и неврологов — головные боли, мигрени, боли в позвоночнике, суставах и периферических нервах.",
      "svc.pain.g1": "Заболевания позвоночника",
      "svc.pain.g1.li1": "Грыжи и протрузии межпозвонковых дисков с болевым синдромом",
      "svc.pain.g1.li2": "Шейная, грудная и пояснично-крестцовая радикулопатия",
      "svc.pain.g1.li3": "Фасеточный синдром (спондилоартроз)",
      "svc.pain.g1.li4": "Хроническая боль в шее и пояснице",
      "svc.pain.g1.li5": "Цервикобрахиалгия и люмбоишиалгия",
      "svc.pain.g1.li6": "Боль при стенозе позвоночного канала",
      "svc.pain.g1.li7": "Боль в крестцово-подвздошном суставе и кокцигодиния",
      "svc.pain.g1.li8": "Хроническая боль после операций на позвоночнике",
      "svc.pain.g2": "Невралгии и периферические нервы",
      "svc.pain.g2.li1": "Невралгия тройничного и затылочного нервов",
      "svc.pain.g2.li2": "Межрёберная и постгерпетическая невралгия",
      "svc.pain.g2.li3": "Невропатия седалищного нерва, синдром грушевидной мышцы",
      "svc.pain.g2.li4": "Туннельные нейропатии (срединный, локтевой, лучевой нервы)",
      "svc.pain.g2.li5": "Посттравматические и послеоперационные нейропатические боли",
      "svc.pain.g2.li6": "Хроническая тазовая и промежностная боль",
      "svc.pain.g3": "Хронические суставные и мышечные боли",
      "svc.pain.g3.li1": "Гонартроз и коксартроз — хроническая боль при артрозе",
      "svc.pain.g3.li2": "Боль в плечевом суставе",
      "svc.pain.g3.li3": "Болевой синдром после эндопротезирования (без механики/инфекции)",
      "svc.pain.g3.li4": "Миофасциальный и мышечно-тонический болевой синдром",
      "svc.pain.g3.li5": "Отдельные формы хронической онкологической боли",
      "svc.pain.g3.li6": "Комплексный регионарный болевой синдром (в рамках комплексного лечения)",
      "svc.pain.g4": "Методы снятия боли",
      "svc.pain.g4.li1": "Лечебно-диагностические блокады — прицельное введение препаратов к источнику боли",
      "svc.pain.g4.li2": "Радиочастотная абляция (РЧА) — воздействие на чувствительные нервные структуры",
      "svc.pain.g4.li3": "Импульсная радиочастотная терапия (PRF) при нейропатической боли",
      "svc.pain.g4.li4": "COSMAN G4 — американское оборудование для малоинвазивного лечения",
      "svc.pain.g4.li5": "Процедуры часто без общего наркоза, короткий период восстановления",
      "svc.pain.metaTitle": "Цель лечения",
      "svc.pain.metaText": "Уменьшить боль, восстановить подвижность и улучшить качество жизни. Метод подбирает врач после обследования; РЧА и блокады показаны не при всех заболеваниях и не всегда устраняют анатомическую причину.",
      "svc.pain.range": "<strong>Оборудование:</strong> COSMAN G4 · малоинвазивные методики",
      "svc.pain.cta": "Записаться на консультацию",
      "contacts.label": "06 · Контакты",
      "contacts.title": "Связь с клиникой",
      "contacts.lead": "Телефон, email и маршрут до клиники — мы ответим в рабочее время и поможем с консультацией или записью.",
      "contacts.asideTitle": "Контактные данные",
      "contacts.asideText": "Колл-центр и координация приёма. Мы ответим в рабочее время и подберём удобный слот.",
      "contacts.phone": "Телефон",
      "contacts.email": "Email",
      "contacts.address": "Адрес",
      "contacts.hours": "Режим работы",
      "contacts.hoursVal": "Пн–Сб 08:00–20:00 · Реанимация 24/7",
      "contacts.mapTitle": "Как добраться",
      "contacts.mapHint": "Выберите карту — маршрут откроется в новой вкладке",
      "maps.2gis": "2ГИС",
      "maps.2gisDesc": "Точная навигация по городу",
      "maps.2gisAlt": "2ГИС",
      "maps.google": "Google Maps",
      "maps.googleDesc": "Маршрут и пробки",
      "maps.googleAlt": "Google Maps",
      "maps.yandex": "Яндекс Карты",
      "maps.yandexDesc": "Навигатор и панорамы",
      "maps.yandexAlt": "Яндекс Карты",
      "maps.open": "Открыть →",
      "maps.route": "2ГИС · маршрут",
      "maps.navAria": "Открыть маршрут в навигаторе",
      "footer.nav": "Навигация",
      "footer.meta": "Реквизиты",
      "footer.legalTitle": "Юридическое предупреждение",
      "footer.legal": "Имеются противопоказания. Необходима консультация специалиста. Информация на сайте носит ознакомительный характер и не является публичной офертой. Цены ориентировочные и могут изменяться. Результаты лечения индивидуальны и зависят от клинической ситуации пациента.",
      "footer.rights": "Все права защищены.",
      "prices.ctaTitle": "Не нашли нужную услугу или хотите уточнить цену?",
      "prices.ctaText": "Свяжитесь с клиникой — администратор подскажет и поможет с записью.",
      "lang.aria": "Выбор языка",
      "doc.burnashev.name": "Бурнашев Марсель Ильдарович",
      "doc.kim.name": "Ким Андрей Афонасьевич",
      "doc.alimov.name": "Алимов Ижод Рустамович",
      "doc.hamrokulov.name": "Хамрокулов Бекзод Баходирович",
      "doc.allarov.name": "Аллаяров Улугбек Джураевич",
      "doc.abdujapparov.name": "Абдужаппаров Сулаймон Бахриддинович",
      "doc.muslimov.name": "Муслимов Улугбек Якубджанович",
    },
    en: {
      "nav.services": "Services",
      "nav.prices": "Price list",
      "nav.doctors": "Doctors",
      "nav.about": "About the clinic",
      "nav.tech": "Technologies",
      "nav.contacts": "Contacts",
      "nav.aria": "Main navigation",
      "nav.mobileAria": "Mobile menu",
      "a11y.skip": "Skip to services",
      "social.instagram": "Instagram",
      "social.instagramAria": "NeurON on Instagram — @neuronmed.uz",
      "social.followTitle": "Follow Us",
      "social.telegram": "Telegram",
      "social.facebook": "Facebook",
      "social.whatsapp": "WhatsApp",
      "social.telegramAria": "NeurON on Telegram — @neuronmedical_center",
      "social.facebookAria": "NeurON on Facebook",
      "social.whatsappAria": "Message on WhatsApp — +998 71 200-00-20",
      "lang.ruTitle": "Russian",
      "lang.uzTitle": "Uzbek",
      "lang.enTitle": "English",
      "footer.legalEntity": "NeurON Medical Centre LLC",
      "header.search": "Search",
      "header.searchAria": "Open site search",
      "header.contacts": "Contacts",
      "header.phoneAria": "Call the clinic",
      "header.burgerAria": "Open menu",
      "header.brandAria": "NeurON Medical Centre — home",
      "prices.catalogIdle": "Catalog: <strong>{n}</strong> services · choose a category or search",
      "prices.idleTitle": "Price list ready to browse",
      "prices.idleText": "Select a category above or type a service name in search to view the price list",
      "prices.showAll": "Show all services",
      "prices.openSearch": "Open search",
      "prices.currency": "Currency: Uzbek sum (UZS) · Tashkent",
      "prices.all": "All",
      "prices.allTitle": "All categories",
      "prices.colService": "Service",
      "prices.colCost": "Price",
      "prices.servicesN": "services",
      "prices.found": "Found: <strong>{n}</strong> of {total} services",
      "prices.emptyTitle": "Nothing found",
      "prices.emptyText": "Try another name or category. If the service you need is not listed — contact the clinic; we will advise and help you book.",
      "prices.reset": "Reset search",
      "prices.filtersAria": "Service categories",
      "prices.searchPh": "Live search: MRI, lab tests, neurosurgery, nerve block…",
      "prices.searchAria": "Live search across the price list",
      "prices.clearAria": "Clear search",
      "prices.legal": "Prices are for information only and may change. Contraindications apply — specialist consultation is required. Final cost is confirmed by the administrator when booking.",
      "prices.loading": "Loading price list…",
      "mobile.search": "Site search",
      "hero.title": "Precise neurosurgery and innovative technologies for your <span>health</span>",
      "hero.lead": "A highly specialized multidisciplinary clinic: neurosurgery, expert-level diagnostics, and minimally invasive procedures.",
      "hero.ctaServices": "Explore specialties",
      "trust.1.title": "Licensed clinic",
      "trust.1.text": "Regulatory documentation and compliance with medical standards",
      "trust.2.title": "Private medical centre",
      "trust.2.text": "Highly specialized multidisciplinary private clinic",
      "trust.3.title": "Evidence base",
      "trust.3.text": "MSCT follow-up of operated patients to confirm quality",
      "trust.4.title": "Full cycle of care",
      "trust.4.text": "Diagnostics → surgery → intensive care → recovery",
      "services.label": "01 · Services",
      "services.title": "Neurosurgery and surgical specialties",
      "services.lead": "Interactive specialties focused on safety, minimally invasive care, and advanced technology. Prices are approximate ranges; exact cost is confirmed after consultation.",
      "services.ctaTitle": "Need advice on a specialty?",
      "services.ctaText": "Call the clinic or email us — we will help you choose a specialist.",
      "svc.neuro.title": "Neurosurgery",
      "svc.neuro.price": "from 8,500,000 UZS",
      "svc.neuro.body": "Full-spectrum neurosurgical care: brain tumors, trauma, vascular pathology, spine and spinal cord disease. Endoscopic spine surgery is a priority focus.",
      "svc.neuro.li1": "Brain and spine tumors",
      "svc.neuro.li2": "Endoscopic spine surgery",
      "svc.neuro.li3": "Vascular diseases of the CNS",
      "svc.neuro.li4": "Degenerative spine disorders",
      "svc.neuro.metaTitle": "Safety",
      "svc.neuro.metaText": "Planning with functional MRI mapping of white-matter tracts. Postoperative MSCT quality control.",
      "svc.neuro.range": "<strong>Range:</strong> consultation from 350,000 · surgery from 8,500,000 UZS",
      "svc.diag.title": "Expert-level diagnostics",
      "svc.diag.price": "from 450,000 UZS",
      "svc.diag.body": "The diagnostic department provides primary and specialized assessment: MRI with functional brain scanning, MSCT, ultrasound, gastro-colonoscopy, laboratory testing, and comprehensive Check-Up programs.",
      "svc.diag.li1": "MRI with functional scanning",
      "svc.diag.li2": "Spiral CT (MSCT)",
      "svc.diag.li3": "Ultrasound and endoscopic diagnostics",
      "svc.diag.li4": "Tissue-level Check-Up",
      "svc.diag.metaTitle": "Technologies",
      "svc.diag.metaText": "Functional MRI assesses the integrity of white-matter tracts — data unavailable on a conventional scanner and critical for neurosurgical planning.",
      "svc.diag.range": "<strong>Range:</strong> from 450,000 to 4,500,000 UZS",
      "svc.angio.title": "Angiography and endovascular procedures",
      "svc.angio.price": "from 6,000,000 UZS",
      "svc.angio.body": "Intravascular procedures without open surgery: coronary angiography, stents, balloon angioplasty, embolization of tumor-feeding vessels, and chemotherapy.",
      "svc.angio.li1": "Coronary angiography and stenting",
      "svc.angio.li2": "Balloon angioplasty of lower-limb vessels",
      "svc.angio.li3": "Uterine artery embolization",
      "svc.angio.li4": "Occlusion of tumor vessels",
      "svc.angio.metaTitle": "Minimally invasive",
      "svc.angio.metaText": "In some cases a tumor process can be controlled by occluding the feeding vessel — without open surgery.",
      "svc.angio.range": "<strong>Range:</strong> from 6,000,000 UZS",
      "svc.surg.title": "Vascular, general, and oncologic surgery",
      "svc.surg.price": "from 5,500,000 UZS",
      "svc.surg.body": "Surgical unit with 40 beds: laser vascular surgery, general surgery, oncology, colorectal surgery, and laparoscopic oncology of the abdomen and pelvis.",
      "svc.surg.li1": "Laser vascular surgery",
      "svc.surg.li2": "Laparoscopic oncology",
      "svc.surg.li3": "Bariatric surgery",
      "svc.surg.li4": "Colorectal surgery",
      "svc.surg.metaTitle": "Infrastructure",
      "svc.surg.metaText": "5 operating theatres with modern equipment and 2 full surgical blocks.",
      "svc.surg.range": "<strong>Range:</strong> from 5,500,000 UZS",
      "svc.plastic.title": "Plastic surgery",
      "svc.plastic.price": "from 7,000,000 UZS",
      "svc.plastic.body": "Plastic procedures using a specialized laser for maximum result quality and controlled tissue trauma.",
      "svc.plastic.li1": "Laser plastic techniques",
      "svc.plastic.li2": "Aesthetic and reconstructive surgery",
      "svc.plastic.li3": "Individual outcome planning",
      "svc.plastic.metaTitle": "Quality",
      "svc.plastic.metaText": "Laser technologies improve precision and aesthetic outcome.",
      "svc.plastic.range": "<strong>Range:</strong> from 7,000,000 UZS",
      "svc.checkF.title": "Women’s Check-Up “Harmony of Health & Beauty”",
      "svc.checkF.price": "2,600,000 UZS",
      "svc.checkF.body": "Full laboratory assessment of key body systems (33 essential markers). Designed with female physiology in mind.",
      "svc.checkF.g1": "Hormonal status",
      "svc.checkF.g1.li1": "Estradiol",
      "svc.checkF.g1.li2": "Prolactin",
      "svc.checkF.g1.li3": "Total testosterone",
      "svc.checkF.g1.li4": "TSH (thyroid-stimulating hormone)",
      "svc.checkF.g1.li5": "Free T4",
      "svc.checkF.g1.li6": "Anti-TPO antibodies",
      "svc.checkF.g1.li7": "Cortisol",
      "svc.checkF.g2": "Metabolism and vitamins",
      "svc.checkF.g2.li1": "Vitamin D (25-OH)",
      "svc.checkF.g2.li2": "Ferritin",
      "svc.checkF.g2.li3": "Serum iron",
      "svc.checkF.g2.li4": "Blood glucose",
      "svc.checkF.g2.li5": "Insulin",
      "svc.checkF.g2.li6": "Total protein",
      "svc.checkF.g3": "Cardiovascular system and lipid profile",
      "svc.checkF.g3.li1": "Total cholesterol",
      "svc.checkF.g3.li2": "LDL (low-density lipoprotein)",
      "svc.checkF.g3.li3": "HDL (high-density lipoprotein)",
      "svc.checkF.g3.li4": "Triglycerides",
      "svc.checkF.g3.li5": "Atherogenic index",
      "svc.checkF.g4": "Kidneys",
      "svc.checkF.g4.li1": "Creatinine",
      "svc.checkF.g4.li2": "Urea",
      "svc.checkF.g4.li3": "Uric acid",
      "svc.checkF.g5": "Liver",
      "svc.checkF.g5.li1": "ALT",
      "svc.checkF.g5.li2": "AST",
      "svc.checkF.g5.li3": "Total bilirubin",
      "svc.checkF.g5.li4": "GGT",
      "svc.checkF.g6": "Inflammation and general screening",
      "svc.checkF.g6.li1": "CRP (C-reactive protein)",
      "svc.checkF.g6.li2": "Complete blood count (CBC)",
      "svc.checkF.g6.li3": "Urinalysis",
      "svc.checkF.g6.li4": "ESR",
      "svc.checkF.g6.li5": "Glycated hemoglobin (HbA1c)",
      "svc.checkF.g6.li6": "Calcium / magnesium (basic mineral profile)",
      "svc.checkF.g6.li7": "Coagulogram (basic clotting markers)",
      "svc.checkF.g6.li8": "Alkaline phosphatase",
      "svc.checkF.metaTitle": "33 markers",
      "svc.checkF.metaText": "The panel covers hormonal balance, metabolism, vascular risks, and kidney and liver function — for early detection of imbalances and support of women’s health.",
      "svc.checkF.range": "<strong>Price:</strong> 2,600,000 UZS",
      "svc.checkM.title": "Men’s Check-Up “Key to Health & Longevity”",
      "svc.checkM.price": "2,900,000 UZS",
      "svc.checkM.body": "Full laboratory assessment with 36 essential markers — focused on vascular risks, metabolism, men’s health, and longevity.",
      "svc.checkM.g1": "Lipid profile and vascular risks",
      "svc.checkM.g1.li1": "Total cholesterol",
      "svc.checkM.g1.li2": "LDL",
      "svc.checkM.g1.li3": "HDL",
      "svc.checkM.g1.li4": "Triglycerides",
      "svc.checkM.g1.li5": "Atherogenic index",
      "svc.checkM.g1.li6": "Homocysteine (when included in the panel)",
      "svc.checkM.g2": "Carbohydrate metabolism",
      "svc.checkM.g2.li1": "Blood glucose",
      "svc.checkM.g2.li2": "Glycated hemoglobin (HbA1c)",
      "svc.checkM.g2.li3": "Insulin",
      "svc.checkM.g2.li4": "HOMA-IR index (calculated)",
      "svc.checkM.g3": "Kidneys and urinary system",
      "svc.checkM.g3.li1": "Creatinine",
      "svc.checkM.g3.li2": "Urea",
      "svc.checkM.g3.li3": "Uric acid",
      "svc.checkM.g3.li4": "Urinalysis",
      "svc.checkM.g4": "Liver and GI tract",
      "svc.checkM.g4.li1": "ALT",
      "svc.checkM.g4.li2": "AST",
      "svc.checkM.g4.li3": "Total bilirubin",
      "svc.checkM.g4.li4": "GGT",
      "svc.checkM.g4.li5": "CEA (carcinoembryonic antigen)",
      "svc.checkM.g5": "Hormonal status and men’s health",
      "svc.checkM.g5.li1": "Total testosterone",
      "svc.checkM.g5.li2": "Prolactin",
      "svc.checkM.g5.li3": "TSH",
      "svc.checkM.g5.li4": "Free T4",
      "svc.checkM.g5.li5": "Total PSA (prostate marker)",
      "svc.checkM.g5.li6": "Cortisol",
      "svc.checkM.g6": "Vitamins, iron, and inflammation",
      "svc.checkM.g6.li1": "Vitamin D (25-OH)",
      "svc.checkM.g6.li2": "Ferritin",
      "svc.checkM.g6.li3": "Serum iron",
      "svc.checkM.g6.li4": "CRP (C-reactive protein)",
      "svc.checkM.g6.li5": "Complete blood count (CBC)",
      "svc.checkM.g6.li6": "ESR",
      "svc.checkM.g6.li7": "Total protein",
      "svc.checkM.g6.li8": "Alkaline phosphatase",
      "svc.checkM.g6.li9": "Coagulogram (basic markers)",
      "svc.checkM.g6.li10": "Magnesium / calcium (mineral profile)",
      "svc.checkM.g6.li11": "Anti-TPO antibodies (when indicated in the panel)",
      "svc.checkM.metaTitle": "36 markers",
      "svc.checkM.metaText": "The program helps assess vascular and metabolic risks, hormonal balance, and longevity resources — with a focus on men’s health.",
      "svc.checkM.range": "<strong>Price:</strong> 2,900,000 UZS",
      "svc.pain.title": "Pain Centre",
      "svc.pain.price": "Pain Management",
      "svc.pain.body": "Modern treatment of chronic and acute pain without open surgery: diagnostic and therapeutic nerve blocks and radiofrequency ablation (RFA) on COSMAN G4 equipment. A combined approach by neurosurgeons and neurologists — headaches, migraine, spine, joint, and peripheral nerve pain.",
      "svc.pain.g1": "Spine disorders",
      "svc.pain.g1.li1": "Disc herniation and protrusion with pain syndrome",
      "svc.pain.g1.li2": "Cervical, thoracic, and lumbosacral radiculopathy",
      "svc.pain.g1.li3": "Facet syndrome (spondylarthrosis)",
      "svc.pain.g1.li4": "Chronic neck and low-back pain",
      "svc.pain.g1.li5": "Cervicobrachialgia and lumboischialgia",
      "svc.pain.g1.li6": "Pain in spinal canal stenosis",
      "svc.pain.g1.li7": "Sacroiliac joint pain and coccygodynia",
      "svc.pain.g1.li8": "Chronic pain after spine surgery",
      "svc.pain.g2": "Neuralgias and peripheral nerves",
      "svc.pain.g2.li1": "Trigeminal and occipital neuralgia",
      "svc.pain.g2.li2": "Intercostal and postherpetic neuralgia",
      "svc.pain.g2.li3": "Sciatic neuropathy, piriformis syndrome",
      "svc.pain.g2.li4": "Entrapment neuropathies (median, ulnar, radial nerves)",
      "svc.pain.g2.li5": "Post-traumatic and postoperative neuropathic pain",
      "svc.pain.g2.li6": "Chronic pelvic and perineal pain",
      "svc.pain.g3": "Chronic joint and muscle pain",
      "svc.pain.g3.li1": "Gonarthrosis and coxarthrosis — chronic pain in osteoarthritis",
      "svc.pain.g3.li2": "Shoulder joint pain",
      "svc.pain.g3.li3": "Pain after joint replacement (without mechanical failure/infection)",
      "svc.pain.g3.li4": "Myofascial and muscle-tone pain syndrome",
      "svc.pain.g3.li5": "Selected forms of chronic cancer-related pain",
      "svc.pain.g3.li6": "Complex regional pain syndrome (as part of multimodal care)",
      "svc.pain.g4": "Pain-relief methods",
      "svc.pain.g4.li1": "Diagnostic and therapeutic blocks — targeted drug delivery to the pain source",
      "svc.pain.g4.li2": "Radiofrequency ablation (RFA) — treatment of sensory nerve structures",
      "svc.pain.g4.li3": "Pulsed radiofrequency therapy (PRF) for neuropathic pain",
      "svc.pain.g4.li4": "COSMAN G4 — U.S. equipment for minimally invasive treatment",
      "svc.pain.g4.li5": "Procedures often without general anesthesia; short recovery period",
      "svc.pain.metaTitle": "Treatment goal",
      "svc.pain.metaText": "Reduce pain, restore mobility, and improve quality of life. The method is chosen by the physician after assessment; RFA and blocks are not indicated for every condition and do not always remove the anatomical cause.",
      "svc.pain.range": "<strong>Equipment:</strong> COSMAN G4 · minimally invasive techniques",
      "svc.pain.cta": "Book a consultation",
      "contacts.label": "06 · Contacts",
      "contacts.title": "Contact the clinic",
      "contacts.lead": "Phone, email, and directions — we reply during business hours and help with consultation or booking.",
      "contacts.asideTitle": "Contact details",
      "contacts.asideText": "Call centre and appointment coordination. We reply during business hours and find a convenient slot.",
      "contacts.phone": "Phone",
      "contacts.email": "Email",
      "contacts.address": "Address",
      "contacts.hours": "Working hours",
      "contacts.hoursVal": "Mon–Sat 08:00–20:00 · ICU 24/7",
      "contacts.mapTitle": "How to get here",
      "contacts.mapHint": "Choose a map — the route opens in a new tab",
      "maps.2gis": "2GIS",
      "maps.2gisDesc": "Precise city navigation",
      "maps.2gisAlt": "2GIS",
      "maps.google": "Google Maps",
      "maps.googleDesc": "Directions and traffic",
      "maps.googleAlt": "Google Maps",
      "maps.yandex": "Yandex Maps",
      "maps.yandexDesc": "Navigator and panoramas",
      "maps.yandexAlt": "Yandex Maps",
      "maps.open": "Open →",
      "maps.route": "2GIS · directions",
      "maps.navAria": "Open directions in a map app",
      "footer.nav": "Navigation",
      "footer.meta": "Details",
      "footer.legalTitle": "Legal notice",
      "footer.legal": "Contraindications apply. Specialist consultation is required. Information on this website is for reference only and is not a public offer. Prices are approximate and may change. Treatment outcomes are individual and depend on the patient’s clinical situation.",
      "footer.rights": "All rights reserved.",
      "prices.ctaTitle": "Can’t find the service you need or want to confirm a price?",
      "prices.ctaText": "Contact the clinic — the administrator will advise and help you book.",
      "lang.aria": "Language selection",
      "doc.burnashev.name": "Marsel Ildarovich Burnashev",
      "doc.kim.name": "Andrey Afonasyevich Kim",
      "doc.alimov.name": "Izhod Rustamovich Alimov",
      "doc.hamrokulov.name": "Bekzod Bakhodirovich Khamrokulov",
      "doc.allarov.name": "Ulugbek Juraevich Allayarov",
      "doc.abdujapparov.name": "Sulaymon Bakhriddinovich Abdujapparov",
      "doc.muslimov.name": "Ulugbek Yakubjanovich Muslimov",
    },
    uz: {
      "nav.services": "Xizmatlar",
      "nav.prices": "Narxlar",
      "nav.doctors": "Shifokorlar",
      "nav.about": "Klinikamiz",
      "nav.tech": "Texnologiyalar",
      "nav.contacts": "Aloqa",
      "nav.aria": "Asosiy navigatsiya",
      "a11y.skip": "Xizmatlarga o‘tish",
      "social.instagram": "Instagram",
      "social.instagramAria": "NeurON Instagram — @neuronmed.uz",
      "social.followTitle": "Ijtimoiy tarmoqlarimiz",
      "social.telegram": "Telegram",
      "social.facebook": "Facebook",
      "social.whatsapp": "WhatsApp",
      "social.telegramAria": "NeurON Telegram — @neuronmedical_center",
      "social.facebookAria": "NeurON Facebook",
      "social.whatsappAria": "WhatsApp orqali yozish — +998 71 200-00-20",
      "lang.ruTitle": "Rus tili",
      "lang.uzTitle": "O‘zbek tili",
      "lang.enTitle": "Ingliz tili",
      "footer.legalEntity": "«NeurON Medical Centre» MChJ",
      "nav.mobileAria": "Mobil menyu",
      "header.search": "Qidiruv",
      "header.searchAria": "Sayt bo‘yicha qidiruvni ochish",
      "header.contacts": "Aloqa",
      "header.phoneAria": "Klinikaga qo‘ng‘iroq qilish",
      "header.burgerAria": "Menyuni ochish",
      "header.brandAria": "NeurON Medical Centre — bosh sahifa",
      "prices.catalogIdle": "Katalogda: <strong>{n}</strong> ta xizmat · kategoriyani yoki qidiruvni tanlang",
      "prices.idleTitle": "Narxlar ro‘yxati ko‘rishga tayyor",
      "prices.idleText": "Yuqoridan kategoriyani tanlang yoki qidiruvga xizmat nomini kiriting — narxlar jadvali ochiladi",
      "prices.showAll": "Barcha xizmatlarni ko‘rsatish",
      "prices.openSearch": "Qidiruvni ochish",
      "prices.currency": "Valyuta: o'zbek so'mi · Toshkent sh.",
      "prices.all": "Hammasi",
      "prices.allTitle": "Barcha kategoriyalar",
      "prices.colService": "Xizmat",
      "prices.colCost": "Narx",
      "prices.servicesN": "ta xizmat",
      "prices.found": "Topildi: <strong>{n}</strong> / {total} ta xizmat",
      "prices.emptyTitle": "Hech narsa topilmadi",
      "prices.emptyText": "Boshqa nom yoki kategoriyani sinab ko‘ring. Kerakli xizmat ro‘yxatda bo‘lmasa — klinikaga murojaat qiling, maslahat beramiz va yozilishda yordam beramiz.",
      "prices.reset": "Qidiruvni tiklash",
      "prices.filtersAria": "Xizmat kategoriyalari",
      "prices.searchPh": "Tirik qidiruv: MRT, tahlillar, neyroxirurgiya, blokada…",
      "prices.searchAria": "Narxlar bo‘yicha tirik qidiruv",
      "prices.clearAria": "Qidiruvni tozalash",
      "prices.legal": "Narxlar axborot xarakteriga ega va o‘zgarishi mumkin. Qarshi ko‘rsatmalar mavjud — mutaxassis konsultatsiyasi zarur. Yakuniy narx yozilishda administrator tomonidan tasdiqlanadi.",
      "prices.loading": "Narxlar yuklanmoqda…",
      "mobile.search": "Sayt bo‘yicha qidiruv",
      "hero.title": "Aniq neyroxirurgiya va innovatsion texnologiyalar — sizning <span>sog‘lig‘ingiz</span> uchun",
      "hero.lead": "Yuqori ixtisoslashgan ko‘p tarmoqli klinika: neyroxirurgiya, ekspert darajadagi diagnostika va kam invaziv aralashuvlar.",
      "hero.ctaServices": "Yo‘nalishlarni ko‘rish",
      "trust.1.title": "Litsenziyalangan klinika",
      "trust.1.text": "Ruxsat hujjatlari va tibbiy standartlarga muvofiqlik",
      "trust.2.title": "Xususiy tibbiyot markazi",
      "trust.2.text": "Yuqori ixtisoslashgan ko‘p tarmoqli xususiy klinika",
      "trust.3.title": "Dalillarga asoslangan yondashuv",
      "trust.3.text": "Sifatni tasdiqlash uchun operatsiya qilingan bemorlarda MSKT nazorati",
      "trust.4.title": "Yordamning to‘liq sikli",
      "trust.4.text": "Diagnostika → jarrohlik → reanimatsiya → tiklanish",
      "services.label": "01 · Xizmatlar",
      "services.title": "Neyroxirurgiya va jarrohlik yo‘nalishlari",
      "services.lead": "Xavfsizlik, kam invazivlik va ilg‘or texnologiyalarga e’tibor qaratilgan interaktiv yo‘nalishlar. Narxlar taxminiy diapazonlar — aniq qiymat konsultatsiyadan so‘ng.",
      "services.ctaTitle": "Yo‘nalish bo‘yicha konsultatsiya kerakmi?",
      "services.ctaText": "Klinikaga qo‘ng‘iroq qiling yoki email yozing — mutaxassis tanlashda yordam beramiz.",
      "svc.neuro.title": "Neyroxirurgiya",
      "svc.neuro.price": "8 500 000 so‘mdan",
      "svc.neuro.body": "Neyroxirurgik yordamning to‘liq spektri: miya o‘smalari, jarohatlar, qon tomir patologiyalari, umurtqa va orqa miya kasalliklari. Umurtqada endoskopik operatsiyalar — ustuvor yo‘nalish.",
      "svc.neuro.li1": "Miya va umurtqa o‘smalari",
      "svc.neuro.li2": "Umurtqaning endoskopik jarrohligi",
      "svc.neuro.li3": "Markaziy asab tizimi qon tomir kasalliklari",
      "svc.neuro.li4": "Umurtqaning degenerativ zararlanishlari",
      "svc.neuro.metaTitle": "Xavfsizlik",
      "svc.neuro.metaText": "O‘tkazuvchi yo‘llarning funktsional MRT-skanerlashini hisobga olgan holda rejalashtirish. Operatsiyadan keyingi MSKT sifat nazorati.",
      "svc.neuro.range": "<strong>Diapazon:</strong> konsultatsiya 350 000 dan · operatsiyalar 8 500 000 so‘mdan",
      "svc.diag.title": "Ekspert darajadagi diagnostika",
      "svc.diag.price": "450 000 so‘mdan",
      "svc.diag.body": "Diagnostika bo‘limi birlamchi va ixtisoslashgan diagnostikani ta’minlaydi: funktsional miya skanerlashli MRT, MSKT, UTT, gastro-kolonoskopiya, laboratoriya va kompleks tekshiruv dasturlari.",
      "svc.diag.li1": "Funktsional skanerlashli MRT",
      "svc.diag.li2": "Spiral KT (MSKT)",
      "svc.diag.li3": "UTT va endoskopik diagnostika",
      "svc.diag.li4": "To‘qima darajasidagi kompleks tekshiruv",
      "svc.diag.metaTitle": "Texnologiyalar",
      "svc.diag.metaText": "Funktsional MRT o‘tkazuvchi yo‘llarning yaxlitligini aniqlaydi — oddiy apparatda mavjud bo‘lmagan ma’lumotlar neyroxirurgiyani rejalashtirish uchun muhim.",
      "svc.diag.range": "<strong>Diapazon:</strong> 450 000 dan 4 500 000 so‘mgacha",
      "svc.angio.title": "Angiografiya va endovaskulyar aralashuvlar",
      "svc.angio.price": "6 000 000 so‘mdan",
      "svc.angio.body": "Ochiq operatsiyasiz qon tomir ichidagi aralashuvlar: koronarografiya, stentlar, tomirlar balon plastikasi, o‘sma oziqlantiruvchi tomirlarni embolizatsiya qilish va kimyoterapiya.",
      "svc.angio.li1": "Koronarografiya va stentlash",
      "svc.angio.li2": "Pastki ekstremitetlar tomirlarining balon plastikasi",
      "svc.angio.li3": "Bachadon arteriyalarini embolizatsiya qilish",
      "svc.angio.li4": "O‘sma tomirlarini yopish",
      "svc.angio.metaTitle": "Kam invazivlik",
      "svc.angio.metaText": "Ba’zi hollarda o‘sma jarayonini oziqlantiruvchi tomirni yopish orqali nazorat qilish mumkin — ochiq operatsiyasiz.",
      "svc.angio.range": "<strong>Diapazon:</strong> 6 000 000 so‘mdan",
      "svc.surg.title": "Qon tomir, umumiy va onkojarrohlik",
      "svc.surg.price": "5 500 000 so‘mdan",
      "svc.surg.body": "40 o‘rinli jarrohlik bo‘limi: lazerli qon tomir jarrohligi, umumiy jarrohlik, onkologiya, koloproktologiya, qorin bo‘shlig‘i va kichik chanoq organlarining laparoskopik onkojarrohligi.",
      "svc.surg.li1": "Lazerli qon tomir jarrohligi",
      "svc.surg.li2": "Laparoskopik onkojarrohlik",
      "svc.surg.li3": "Bariatrik operatsiyalar",
      "svc.surg.li4": "Koloproktologiya",
      "svc.surg.metaTitle": "Infrastruktura",
      "svc.surg.metaText": "Eng yangi uskunali 5 ta operatsiya zali va 2 ta operatsiya bloki.",
      "svc.surg.range": "<strong>Diapazon:</strong> 5 500 000 so‘mdan",
      "svc.plastic.title": "Plastik jarrohlik",
      "svc.plastic.price": "7 000 000 so‘mdan",
      "svc.plastic.body": "Natija sifati maksimal va to‘qimalarga nazoratli shikast yetkazish uchun maxsus lazer qo‘llaniladigan plastik aralashuvlar.",
      "svc.plastic.li1": "Lazerli plastik usullar",
      "svc.plastic.li2": "Estetik va rekonstruktiv jarrohlik",
      "svc.plastic.li3": "Natijani individual rejalashtirish",
      "svc.plastic.metaTitle": "Sifat",
      "svc.plastic.metaText": "Lazer texnologiyalari aralashuvning aniqligi va estetik natijasini oshiradi.",
      "svc.plastic.range": "<strong>Diapazon:</strong> 7 000 000 so‘mdan",
      "svc.checkF.title": "Ayollar uchun check-up «Salomatlik va go‘zallik uyg‘unligi»",
      "svc.checkF.price": "2 600 000 so‘m",
      "svc.checkF.body": "Ayollar organizmining 33 ta asosiy ko‘rsatkichi bo‘yicha to‘liq laboratoriya diagnostikasi (gormonlar, vitamin D, temir, moddalar almashinuvi, qalqonsimon bez va b.).",
      "svc.checkF.g1": "Gormonal holat",
      "svc.checkF.g1.li1": "Estradiol",
      "svc.checkF.g1.li2": "Prolaktin",
      "svc.checkF.g1.li3": "Umumiy testosteron",
      "svc.checkF.g1.li4": "TTG (tireotrop gormon)",
      "svc.checkF.g1.li5": "Erkin T4",
      "svc.checkF.g1.li6": "TPO ga antitanachalar (Anti-TPO)",
      "svc.checkF.g1.li7": "Kortizol",
      "svc.checkF.g2": "Moddalar almashinuvi va vitaminlar",
      "svc.checkF.g2.li1": "D vitamini (25-OH)",
      "svc.checkF.g2.li2": "Ferritin",
      "svc.checkF.g2.li3": "Zardob temiri",
      "svc.checkF.g2.li4": "Qon glyukozasi",
      "svc.checkF.g2.li5": "Insulin",
      "svc.checkF.g2.li6": "Umumiy oqsil",
      "svc.checkF.g3": "Yurak-qon tomir tizimi va lipid profili",
      "svc.checkF.g3.li1": "Umumiy xolesterin",
      "svc.checkF.g3.li2": "LPNP (past zichlikdagi lipoproteinlar)",
      "svc.checkF.g3.li3": "LPVP (yuqori zichlikdagi lipoproteinlar)",
      "svc.checkF.g3.li4": "Triglitseridlar",
      "svc.checkF.g3.li5": "Aterogenlik koeffitsienti",
      "svc.checkF.g4": "Buyraklar",
      "svc.checkF.g4.li1": "Kreatinin",
      "svc.checkF.g4.li2": "Mochevina",
      "svc.checkF.g4.li3": "Siydik kislotasi",
      "svc.checkF.g5": "Jigar",
      "svc.checkF.g5.li1": "ALT",
      "svc.checkF.g5.li2": "AST",
      "svc.checkF.g5.li3": "Umumiy bilirubin",
      "svc.checkF.g5.li4": "GGT",
      "svc.checkF.g6": "Yallig‘lanish va umumiy tekshiruv",
      "svc.checkF.g6.li1": "SRP (C-reaktiv oqsil)",
      "svc.checkF.g6.li2": "Umumiy qon tahlili (UQT)",
      "svc.checkF.g6.li3": "Umumiy siydik tahlili (UST)",
      "svc.checkF.g6.li4": "ECHT",
      "svc.checkF.g6.li5": "Glikirlangan gemoglobin (HbA1c)",
      "svc.checkF.g6.li6": "Kalsiy / magniy (asosiy mineral profil)",
      "svc.checkF.g6.li7": "Koagulogramma (asosiy ko‘rsatkichlar)",
      "svc.checkF.g6.li8": "Ishqoriy fosfataza",
      "svc.checkF.metaTitle": "33 ko‘rsatkich",
      "svc.checkF.metaText": "Majmua gormonal fon, moddalar almashinuvi, tomir xavflari, buyrak va jigar funksiyasini hisobga oladi — nomutanosibliklarni erta aniqlash va ayollar sog‘lig‘ini qo‘llab-quvvatlash uchun.",
      "svc.checkF.range": "<strong>Narxi:</strong> 2 600 000 so‘m",
      "svc.checkM.title": "Erkaklar uchun check-up «Salomatlik va uzoq umr ko‘rish kaliti»",
      "svc.checkM.price": "2 900 000 so‘m",
      "svc.checkM.body": "Organizmning 36 ta muhim ko‘rsatkichi bo‘yicha to‘liq diagnostikasi (yurak-qon tomir tizimi, testosteron, jigar, buyraklar, moddalar almashinuvi).",
      "svc.checkM.g1": "Lipid profili va tomir xavflari",
      "svc.checkM.g1.li1": "Umumiy xolesterin",
      "svc.checkM.g1.li2": "LPNP",
      "svc.checkM.g1.li3": "LPVP",
      "svc.checkM.g1.li4": "Triglitseridlar",
      "svc.checkM.g1.li5": "Aterogenlik koeffitsienti",
      "svc.checkM.g1.li6": "Homotsistein (panelda mavjud bo‘lsa)",
      "svc.checkM.g2": "Uglevod almashinuvi",
      "svc.checkM.g2.li1": "Qon glyukozasi",
      "svc.checkM.g2.li2": "Glikirlangan gemoglobin (HbA1c)",
      "svc.checkM.g2.li3": "Insulin",
      "svc.checkM.g2.li4": "HOMA-IR indeksi (hisobiy)",
      "svc.checkM.g3": "Buyraklar va siydik chiqarish tizimi",
      "svc.checkM.g3.li1": "Kreatinin",
      "svc.checkM.g3.li2": "Mochevina",
      "svc.checkM.g3.li3": "Siydik kislotasi",
      "svc.checkM.g3.li4": "Umumiy siydik tahlili (UST)",
      "svc.checkM.g4": "Jigar va oshqozon-ichak tizimi",
      "svc.checkM.g4.li1": "ALT",
      "svc.checkM.g4.li2": "AST",
      "svc.checkM.g4.li3": "Umumiy bilirubin",
      "svc.checkM.g4.li4": "GGT",
      "svc.checkM.g4.li5": "CEA (saraton embrional antigeni)",
      "svc.checkM.g5": "Gormonal holat va erkaklar sog‘lig‘i",
      "svc.checkM.g5.li1": "Umumiy testosteron",
      "svc.checkM.g5.li2": "Prolaktin",
      "svc.checkM.g5.li3": "TTG",
      "svc.checkM.g5.li4": "Erkin T4",
      "svc.checkM.g5.li5": "Umumiy PSA (prostata bezining markeri)",
      "svc.checkM.g5.li6": "Kortizol",
      "svc.checkM.g6": "Vitaminlar, temir va yallig‘lanish",
      "svc.checkM.g6.li1": "D vitamini (25-OH)",
      "svc.checkM.g6.li2": "Ferritin",
      "svc.checkM.g6.li3": "Zardob temiri",
      "svc.checkM.g6.li4": "SRP (C-reaktiv oqsil)",
      "svc.checkM.g6.li5": "Umumiy qon tahlili (UQT)",
      "svc.checkM.g6.li6": "ECHT",
      "svc.checkM.g6.li7": "Umumiy oqsil",
      "svc.checkM.g6.li8": "Ishqoriy fosfataza",
      "svc.checkM.g6.li9": "Koagulogramma (asosiy ko‘rsatkichlar)",
      "svc.checkM.g6.li10": "Magniy / kalsiy (mineral profil)",
      "svc.checkM.g6.li11": "TPO ga antitanachalar (panelda ko‘rsatilganda)",
      "svc.checkM.metaTitle": "36 ko‘rsatkich",
      "svc.checkM.metaText": "Dastur tomir va metabolik xavflarni, gormonal muvozanatni va uzoq umr resursini baholashga yordam beradi — erkaklar sog‘lig‘iga urg‘u bilan.",
      "svc.checkM.range": "<strong>Narxi:</strong> 2 900 000 so‘m",
      "svc.pain.title": "Og‘riq markazi (Og‘riqni davolash markazi)",
      "svc.pain.price": "Og‘riqni davolash",
      "svc.pain.body": "Bosh og‘riqlari, migren, umurtqa pog‘onasi, bo‘g‘im va asab og‘riqlarini kompleks davolash, kam invaziv blokadalar hamda reabilitatsiya.",
      "svc.pain.g1": "Umurtqa kasalliklari",
      "svc.pain.g1.li1": "Og‘riq sindromli umurtqa disklarining churrasi va protruziyasi",
      "svc.pain.g1.li2": "Bo‘yin, ko‘krak va bel-dumg‘aza radikalopatiyasi",
      "svc.pain.g1.li3": "Faset sindromi (spondiloartroz)",
      "svc.pain.g1.li4": "Bo‘yin va belda surunkali og‘riq",
      "svc.pain.g1.li5": "Servikobraxialgiya va lumboshiyalgiya",
      "svc.pain.g1.li6": "Umurtqa kanal stenozida og‘riq",
      "svc.pain.g1.li7": "Sakroiliak bo‘g‘im og‘rig‘i va koksigodiniya",
      "svc.pain.g1.li8": "Umurtqa operatsiyalaridan keyingi surunkali og‘riq",
      "svc.pain.g2": "Nevralgiya va periferik nervlar",
      "svc.pain.g2.li1": "Uch shoxli va ensa nervlari nevralgiyasi",
      "svc.pain.g2.li2": "Qovurg‘alararo va postgerpetik nevralgiya",
      "svc.pain.g2.li3": "Chanoq nervi nevropatiyasi, noksimon muskul sindromi",
      "svc.pain.g2.li4": "Tunnel nevropatiyalari (o‘rta, tirsak, nur nervlari)",
      "svc.pain.g2.li5": "Travma va operatsiyadan keyingi nevropatik og‘riqlar",
      "svc.pain.g2.li6": "Surunkali chanoq va perineal og‘riq",
      "svc.pain.g3": "Surunkali bo‘g‘im va mushak og‘riqlari",
      "svc.pain.g3.li1": "Gonartroz va koksartroz — artrozda surunkali og‘riq",
      "svc.pain.g3.li2": "Yelka bo‘g‘imidagi og‘riq",
      "svc.pain.g3.li3": "Endoprotezdan keyingi og‘riq sindromi (mexanika/infeksiyasiz)",
      "svc.pain.g3.li4": "Miofasial va mushak-tonik og‘riq sindromi",
      "svc.pain.g3.li5": "Surunkali onkologik og‘riqning alohida shakllari",
      "svc.pain.g3.li6": "Kompleks regional og‘riq sindromi (majmuaviy davolash doirasida)",
      "svc.pain.g4": "Og‘riqni bartaraf etish usullari",
      "svc.pain.g4.li1": "Davolash-diagnostika blokadalari — dori vositalarini og‘riq manbaiga nishonga kiritish",
      "svc.pain.g4.li2": "Radiochastotali ablyatsiya (RChA) — sezuvchi nerv tuzilmalariga ta’sir",
      "svc.pain.g4.li3": "Impulsli radiochastotali terapiya (PRF) nevropatik og‘riqda",
      "svc.pain.g4.li4": "COSMAN G4 — kam invaziv davolash uchun Amerika uskunasi",
      "svc.pain.g4.li5": "Ko‘pincha umumiy narkozsiz, qisqa tiklanish davri",
      "svc.pain.metaTitle": "Davolash maqsadi",
      "svc.pain.metaText": "Og‘riqni kamaytirish, harakatchanlikni tiklash va hayot sifatini yaxshilash. Usulni shifokor tekshiruvdan keyin tanlaydi; RChA va blokadalar barcha kasalliklarda ko‘rsatilmaydi va har doim anatomik sababni bartaraf etmaydi.",
      "svc.pain.range": "<strong>Uskuna:</strong> COSMAN G4 · kam invaziv usullar",
      "svc.pain.cta": "Konsultatsiyaga yozilish",
      "contacts.label": "06 · Aloqa",
      "contacts.title": "Klinika bilan bog‘lanish",
      "contacts.lead": "Telefon, email va klinikagacha marshrut — ish vaqtida javob beramiz, konsultatsiya yoki yozilishda yordam beramiz.",
      "contacts.asideTitle": "Aloqa ma’lumotlari",
      "contacts.asideText": "Call-markaz va qabulni muvofiqlashtirish. Ish vaqtida javob beramiz va qulay vaqtni tanlaymiz.",
      "contacts.phone": "Telefon",
      "contacts.email": "Email",
      "contacts.address": "Manzil",
      "contacts.hours": "Ish vaqti",
      "contacts.hoursVal": "Du–Sh 08:00–20:00 · Reanimatsiya 24/7",
      "contacts.mapTitle": "Qanday yetib borish mumkin",
      "contacts.mapHint": "Xaritani tanlang — marshrut yangi tabda ochiladi",
      "maps.2gis": "2GIS",
      "maps.2gisDesc": "Shahar bo‘yicha aniq navigatsiya",
      "maps.2gisAlt": "2GIS",
      "maps.google": "Google Maps",
      "maps.googleDesc": "Marshrut va tirbandlik",
      "maps.googleAlt": "Google Maps",
      "maps.yandex": "Yandex Xaritalar",
      "maps.yandexDesc": "Navigator va panoramalar",
      "maps.yandexAlt": "Yandex Xaritalar",
      "maps.open": "Ochish →",
      "maps.route": "2GIS · marshrut",
      "maps.navAria": "Navigatorida marshrutni ochish",
      "footer.nav": "Navigatsiya",
      "footer.meta": "Rekvizitlar",
      "footer.legalTitle": "Huquqiy ogohlantirish",
      "footer.legal": "Qarshi ko‘rsatmalar mavjud. Mutaxassis konsultatsiyasi zarur. Saytdagi ma’lumot tanishuv xarakteriga ega va ommaviy oferta hisoblanmaydi. Narxlar taxminiy va o‘zgarishi mumkin. Davolash natijalari individual va bemor klinik holatiga bog‘liq.",
      "footer.rights": "Barcha huquqlar himoyalangan.",
      "prices.ctaTitle": "Kerakli xizmatni topmadingizmi yoki narxni aniqlashtirmoqchimisiz?",
      "prices.ctaText": "Klinikaga murojaat qiling — administrator maslahat beradi va yozilishda yordam beradi.",
      "lang.aria": "Tilni tanlash",
      "doc.burnashev.name": "Burnashev Marsel Ildaovich",
      "doc.kim.name": "Kim Andrey Afonasevich",
      "doc.alimov.name": "Alimov Ijod Rustamovich",
      "doc.hamrokulov.name": "Xamrokulov Bekzod Baxodirovich",
      "doc.allarov.name": "Allayarov Ulugbek Juraevich",
      "doc.abdujapparov.name": "Abdujapparov Salaymon Baxriddinovich",
      "doc.muslimov.name": "Muslimov Ulugbek Yakubjanovich",
    }
  };

  /* Merge page extras (doctors roles/bios, about, tech…) over core DICT */
  function mergeExtra() {
    const extra = window.NEURON_I18N_EXTRA || { ru: {}, uz: {}, en: {} };
    Object.assign(DICT.ru, extra.ru || {});
    Object.assign(DICT.uz, extra.uz || {});
    DICT.en = DICT.en || {};
    Object.assign(DICT.en, extra.en || {});
  }
  mergeExtra();

  function detectLang() {
    const params = new URLSearchParams(location.search);
    const fromQuery = (params.get("lang") || "").toLowerCase();
    if (SUPPORTED.includes(fromQuery)) return fromQuery;
    try {
      const stored = (localStorage.getItem(STORAGE_KEY) || "").toLowerCase();
      if (SUPPORTED.includes(stored)) return stored;
    } catch (_) { /* ignore */ }
    return "uz";
  }

  function t(lang, key) {
    return (DICT[lang] && DICT[lang][key]) || (DICT.ru && DICT.ru[key]) || null;
  }

  function getLang() {
    const attr = (document.documentElement.getAttribute("data-lang") || "").toLowerCase();
    if (SUPPORTED.includes(attr)) return attr;
    return detectLang();
  }

  function tc(key, vars) {
    let val = t(getLang(), key);
    if (val == null) return key;
    if (vars && typeof vars === "object") {
      Object.keys(vars).forEach((k) => {
        val = val.replace(new RegExp("\\{" + k + "\\}", "g"), String(vars[k]));
      });
    }
    return val;
  }

  function priceMap() {
    return window.NEURON_PRICE_I18N || { categories: {}, short: {}, items: {} };
  }

  function localizeCategory(cat, { short } = {}) {
    if (getLang() === "en") {
      const enMap = {
        "Биохимические анализы": "Biochemistry",
        "Гематология и трансфузиология": "Hematology",
        "Иммунофлюоресцентный анализ и ревмопробы": "Immunology",
        "ИХЛА — гормоны, инфекции, маркеры": "Hormones / IHLA",
        "Клинические анализы": "Clinical labs",
        "Коагулограмма": "Coagulation",
        "Онкомаркеры": "Tumor markers",
        "Лучевая диагностика — МРТ": "MRI",
        "Лучевая диагностика — МСКТ (КТ)": "MSCT",
        "Нейрохирургия": "Neurosurgery"
      };
      return enMap[cat] || cat;
    }
    if (getLang() !== "uz") {
      if (short) {
        const ruShort = {
          "Биохимические анализы": "Биохимия",
          "Гематология и трансфузиология": "Гематология",
          "Иммунофлюоресцентный анализ и ревмопробы": "Иммунология",
          "ИХЛА — гормоны, инфекции, маркеры": "ИХЛА / гормоны",
          "Клинические анализы": "Клиника",
          "Коагулограмма": "Коагулограмма",
          "Онкомаркеры": "Онкомаркеры",
          "Лучевая диагностика — МРТ": "МРТ",
          "Лучевая диагностика — МСКТ (КТ)": "МСКТ",
          "Нейрохирургия": "Нейрохирургия"
        };
        return ruShort[cat] || cat;
      }
      return cat;
    }
    const map = priceMap();
    if (short) return (map.short && map.short[cat]) || (map.categories && map.categories[cat]) || cat;
    return (map.categories && map.categories[cat]) || cat;
  }

  function localizeItemName(name) {
    if (getLang() === "en" || getLang() !== "uz") return name;
    const map = priceMap();
    return (map.items && map.items[name]) || name;
  }

  function localizePriceValue(price) {
    const s = String(price == null ? "" : price);
    if (getLang() === "en") return s.replace(/сум/gi, "UZS");
    if (getLang() !== "uz") return s;
    return s.replace(/сум/gi, "so‘m");
  }

  function setMetaContent(selector, content) {
    const el = document.querySelector(selector);
    if (el) el.setAttribute("content", content);
  }

  function applyMeta(lang) {
    const m = META[lang] || META.ru;
    document.title = m.title;
    setMetaContent('meta[name="description"]', m.description);
    setMetaContent('meta[name="keywords"]', m.keywords || "");
    setMetaContent('meta[property="og:title"]', m.title);
    setMetaContent('meta[property="og:description"]', m.description);
    setMetaContent('meta[property="og:locale"]', m.ogLocale);
    setMetaContent('meta[property="og:url"]', m.ogUrl);
    setMetaContent('meta[name="twitter:title"]', m.title);
    setMetaContent('meta[name="twitter:description"]', m.description);
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) canonical.setAttribute("href", m.ogUrl);
    document.querySelectorAll('link[rel="alternate"][hreflang]').forEach((link) => {
      const hl = (link.getAttribute("hreflang") || "").toLowerCase();
      if (hl === "ru") link.setAttribute("href", META.ru.ogUrl);
      if (hl === "uz") link.setAttribute("href", META.uz.ogUrl);
      if (hl === "en") link.setAttribute("href", META.en.ogUrl);
      if (hl === "x-default") link.setAttribute("href", META.uz.ogUrl);
    });
  }

  function applyTranslations(lang) {
    mergeExtra();
    const htmlLang = lang === "uz" ? "uz" : lang === "en" ? "en" : "ru";
    document.documentElement.lang = htmlLang;
    document.documentElement.setAttribute("data-lang", lang);

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const val = t(lang, key);
      if (val != null) el.textContent = val;
    });

    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const key = el.getAttribute("data-i18n-html");
      const val = t(lang, key);
      if (val != null) el.innerHTML = val;
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      const val = t(lang, key);
      if (val != null) el.setAttribute("placeholder", val);
    });

    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      const key = el.getAttribute("data-i18n-aria");
      const val = t(lang, key);
      if (val != null) el.setAttribute("aria-label", val);
    });
    document.querySelectorAll("[data-i18n-title]").forEach((el) => {
      const key = el.getAttribute("data-i18n-title");
      const val = t(lang, key);
      if (val != null) el.setAttribute("title", val);
    });
    document.querySelectorAll("[data-i18n-alt]").forEach((el) => {
      const key = el.getAttribute("data-i18n-alt");
      const val = t(lang, key);
      if (val != null) el.setAttribute("alt", val);
    });


    document.querySelectorAll("[data-lang-set]").forEach((btn) => {
      const active = btn.getAttribute("data-lang-set") === lang;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });

    applyMeta(lang);
  }

  function setLang(lang, { pushUrl } = { pushUrl: true }) {
    if (!SUPPORTED.includes(lang)) lang = "uz";
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (_) { /* ignore */ }

    if (pushUrl) {
      const url = new URL(location.href);
      url.searchParams.set("lang", lang);
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    }

    applyTranslations(lang);
    window.dispatchEvent(new CustomEvent("neuron:langchange", { detail: { lang } }));
  }

  function init() {
    const lang = detectLang();
    applyTranslations(lang);

    document.querySelectorAll("[data-lang-set]").forEach((btn) => {
      btn.addEventListener("click", () => {
        setLang(btn.getAttribute("data-lang-set") || "ru");
      });
    });

    // Sync URL if missing lang param (keeps shareable links)
    const params = new URLSearchParams(location.search);
    if (!params.get("lang")) {
      const url = new URL(location.href);
      url.searchParams.set("lang", lang);
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    }
  }

  window.NeuronI18n = {
    setLang,
    detectLang,
    getLang,
    t,
    tc,
    localizeCategory,
    localizeItemName,
    localizePriceValue,
    META,
    DICT
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
