#!/usr/bin/env python3
"""
Tool to enrich docs/sprint27_campaign.json with Threads viral strategy,
copywriting angles, specifications, and platform strategies compliant with Gathot standards.
"""
import json
from datetime import datetime, timezone

def generate_sprint27_data():
    with open("docs/sprint27_campaign.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    affiliate_url = "https://s.shopee.co.id/2BFO1kXcTq"

    data["status"] = "ready_for_campaign"
    data["affiliate_url"] = affiliate_url
    data["specs"] = [
        "Dual Display: Kombinasi dial analog kuarsa presisi dan layar digital LED modern untuk kemudahan membaca waktu sekaligus",
        "Fitur Chronograph & Multi-fungsi: Dilengkapi stopwatch, kalender otomatis tanggal & hari, serta alarm harian terintegrasi",
        "Water Resistant (Tahan Air): Aman dari cipratan air hujan, keringat, dan aktivitas harian seperti cuci tangan",
        "Lampu LED Backlight: Angka digital dan jarum luminer menyala terang di kondisi minim cahaya atau malam hari",
        "Rugged & Sporty Casing: Bodi kokoh tahan benturan ringan dengan strap silikon/karet yang fleksibel dan ergonomis di pergelangan tangan",
        "Desain Tactical Maskulin: Tampilan dial bergaya militer modern yang memberi impresi solid, sporty, dan percaya diri"
    ]

    campaign_strategy = {
        "target_audience": "Pria aktif, komuter harian, pekerja outdoor maupun kantoran, mahasiswa, dan peminat jam tangan tactical sporty yang menginginkan jam tangan maskulin tangguh berfitur lengkap tanpa menguras dompet.",
        "key_selling_points": [
            "Tampilan dual display tangguh: gabungan analog kuarsa dan digital LED yang maskulin dan sporty",
            "Fitur multi-fungsi praktis: stopwatch, kalender otomatis, alarm, dan lampu LED untuk navigasi waktu instan",
            "Daya tahan water resistant harian: tenang saat kehujanan di jalan atau kena cipratan air",
            "Strap ergonomis fleksibel yang nyaman dipakai berjam-jam saat riding, olahraga, maupun aktivitas kerja harian",
            "Value for money tinggi: estetika jam tactical puluhan kali lipat dari harga aslinya"
        ],
        "threads_viral_strategy": {
            "compliance": "Sesuai standar Gathot: Tanpa klaim konsumsi pribadi palsu ('aku/saya sudah pakai'), tanpa emoji berlebihan, karakter Threads <= 500 per post, link affiliate resmi Shopee, hashtag terarah 3-5 tags.",
            "core_narrative": "Mengangkat observasi relatable seputar pria yang sering cemas jam tangannya rusak kena hujan saat riding atau terbentur saat aktivitas lapangan, lalu menghadirkan kurasi objektif jam tangan dual display tangguh berpenampilan gagah.",
            "framework": "2-Post Thread Split (Post 1: Situational Hook / Dilemma -> Post 2: Curated Specs & Soft CTA Shopee)"
        }
    }

    copywriting_angles = [
        {
            "angle_id": "angle-01",
            "angle_name": "Dilema Jam Ringkih Saat Riding & Kehujanan di Jalan",
            "angle_description": "Menyasar pria pengendara motor dan komuter harian yang sering was-was jam tangannya kemasukan air saat hujan mendadak atau rusak kena benturan ringan.",
            "emotional_hook": "Rasa panik saat riding tiba-tiba diguyur hujan dan buru-buru menyelamatkan jam tangan ke dalam saku. Solusinya adalah jam sport tangguh tahan air yang siap tempur di jalanan.",
            "posts": {
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Lagi asyik riding tiba-tiba langit mendung dan hujan deras turun. 🌧️\n\nHal pertama yang bikin panik sering bukan jas hujan, tapi jam tangan yang buru-buru dilepas terus diselipin ke saku celana karena takut kemasukan air.\n\nPria yang mobilitasnya tinggi di jalan memang butuh jam tangan tahan banting yang gak manja sama air dan benturan ringan.",
                        "visual_note": "Foto sprint27_product_1.jpg: Tampilan jam tangan sport LIGE tahan air dengan dial gahar"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi spek LIGE Jam Tangan Sport Dual Display:\n\n- Dual Time: Analog kuarsa + digital LED presisi\n- Water Resistant: Tenang saat kena hujan & cipratan air\n- Fitur Komplit: Stopwatch, alarm, tanggal & hari\n- LED Backlight: Tetap jelas dibaca saat malam\n- Strap Karet Sporty: Nyaman & fleksibel di tangan\n\nTampilan maskulin dan kokoh buat aktivitas harian.\nCek ketersediaan di Shopee: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganPria #JamTanganSport #AksesorisPria #JamPriaKeren",
                        "visual_note": "Foto sprint27_product_2.jpg: Detail dial ganda dan tombol fungsi samping yang kokoh"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Pernah ngalamin lagi riding santai di sore hari, tiba-tiba langit berubah gelap dan hujan turun deras tanpa aba-aba?\n\nRefleks pertama kebanyakan cowok sering kali bukan neduh, tapi panik melepas jam tangan kulit atau jam ringkihnya lalu diselipin ke dalam saku celana biar gak mati kemasukan air.\n\nMemang beda rasanya kalau di pergelangan tangan terpasang jam tahan banting yang siap diajak tempur di segala cuaca tanpa rasa was-was.",
                        "visual_note": "Foto kolase sprint27_product_1.jpg dan sprint27_product_4.jpg: Jam tangan saat outdoor"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi spesifikasi teknis LIGE Dual Display Sport Chronograph Watch:\n\n- Mesin Dual Display: Penggabungan jarum analog kuarsa dan layar digital LED multifungsi\n- Fitur Lengkap: Stopwatch pengukur waktu, kalender hari/tanggal otomatis, dan alarm terintegrasi\n- Daya Tahan Air (Water Resistant): Aman dari terpaan air hujan, keringat deras saat berolahraga, dan cipratan cuci tangan\n- Fitur Backlight LED: Jarum luminer dan angka digital terang benderang di area gelap\n- Strap Silikon Lembut: Tidak menyebabkan iritasi kulit meski dipakai berkeringat seharian\n\nPilihan praktis bagi yang butuh jam tangan tangguh untuk aktivitas kerja harian maupun touring.\nLink belanja resmi Shopee: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganPria #JamTanganAntiAir #AksesorisPria #JamTactical #RidingGear",
                        "visual_note": "Foto sprint27_product_6.jpg: Tampilan close-up fitur chronograph dan tombol operasional"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Jam tangan yang gak bikin was-was pas mendadak diguyur hujan di jalan. 🌧️\n\nSering kali cowok butuh satu jam tempur yang gak manja. Kena air hujan aman, kena benturan ringan tetap solid, dan tampilannya tetap bikin pergelangan tangan kelihatan gagah berisi.\n\nSwipe ke samping buat kurasi fitur dual display dan konstruksinya. 👉",
                        "visual_note": "Carousel Slide 1: sprint27_product_1.jpg (Foto produk resolusi tinggi dengan aura gagah)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Detail spesifikasi LIGE Men's Dual Display Watch:\n\n- Dual Display: Analog Quartz presisi tinggi + Digital LED\n- Water Resistant harian tahan cipratan hujan & air\n- Fitur Multifungsi: Stopwatch, kalender harian, & alarm\n- LED Backlight terang di kondisi minim cahaya\n- Strap karet sporty lentur dan kokoh\n\nPerpaduan estetika tactical militer modern dengan durabilitas tinggi.\nLink belanja Shopee: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganPria #JamTanganSporty #JamTactical #OOTDCowok #AksesorisPria",
                        "visual_note": "Carousel Slide 2 & 3: sprint27_product_3.jpg dan sprint27_product_5.jpg detail visual dan strap"
                    }
                }
            }
        },
        {
            "angle_id": "angle-02",
            "angle_name": "Tampilan Tactical Maskulin Tanpa Jebol Dompet",
            "angle_description": "Menyasar pria yang ingin upgrade penampilan maskulin dengan aksesoris bertema tactical militer tanpa harus merogoh kocek jutaan rupiah.",
            "emotional_hook": "Keinginan tampil gagah dan berkarakter saat memakai outfit kasual atau kerja, namun realistis dengan anggaran belanja harian.",
            "posts": {
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Kadang pengin tampilan jam tangan yang kelihatan gahar dan berkarakter di pergelangan tangan. ⌚\n\nBukan buat pamer kemewahan, tapi biar pas dipadu sama jaket bomber atau kaos polos tetap kelihatan tegas dan berisi.\n\nProblemnya, jam tactical outdoor sering dipatok jutaan rupiah padahal fungsinya cuma buat tempur harian di jalanan kota.",
                        "visual_note": "Foto sprint27_product_3.jpg: Sudut pengambilan visual dial tebal maskulin"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Alternatif jam tactical terjangkau dengan LIGE Dual Display:\n\n- Bodi solid tahan benturan ringan bergaya militer\n- Mesin dual quartz + digital LED aktif\n- Chronograph stopwatch & alarm multifungsi\n- Water resistant untuk cipratan hujan & cuci tangan\n- Backlight LED terang di ruangan gelap\n\nDesain gagah tanpa bikin saldo rekening menangis.\nLink belanja Shopee: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganSporty #JamPriaMurah #JamTactical #FashionPria",
                        "visual_note": "Foto sprint27_product_7.jpg: Detail case dan bezel bergerigi bergaya tactical"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Banyak pria setuju kalau jam tangan adalah satu-satunya aksesoris yang paling efektif mengubah aura penampilan secara instan.\n\nKaos polos dan celana jeans biasa bisa mendadak kelihatan maskulin dan rapi hanya dengan menambahkan jam tangan berdesain kokoh di pergelangan tangan.\n\nTantangannya adalah menemukan jam berdesain tactical kokoh yang harganya masuk akal namun tetap awet dipakai mobilitas tinggi.",
                        "visual_note": "Foto kolase sprint27_product_8.jpg dan sprint27_product_9.jpg: Jam tangan dipadukan outfit kasual"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi keunggulan LIGE Dual Display Watch untuk upgrade gaya harian:\n\n- Estetika Maskulin Kokoh: Bezel berkarakter dengan aksen baut industri yang memberi impresi kuat dan percaya diri\n- Sistem Waktu Ganda (Dual Time): Membaca waktu format analog jarum dan angka digital sekilas pandang\n- Fitur Aktif: Stopwatch presisi, alarm pengingat agenda, dan tampilan tanggal lengkap\n- Tahan Air (Water Resistant): Tidak perlu cemas saat mencuci tangan atau berkeringat di tempat kerja\n- Ergonomis: Bobot seimbang, tidak membuat pergelangan tangan pegal saat berkendara jauh\n\nSolusi tepat tampil tangguh dan maskulin dengan anggaran yang sangat bersahabat.\nLink pembelian Shopee: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamPria #GayaMaskulin #JamOutdoor #FashionPria #JamKeren",
                        "visual_note": "Foto sprint27_product_10.jpg: Foto close up dial dengan tekstur tajam"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Upgrade aura maskulin gak harus bikin tabungan terkuras. ⚡\n\nKombinasi dial analog kuarsa dan LED digital bergaya tactical ini memberi impresi tegas di pergelangan tangan, cocok buat padu padan outfit kasual maupun motoran.\n\nGeser untuk melihat detail bodi dan spesifikasi lengkapnya. 👉",
                        "visual_note": "Carousel Slide 1: sprint27_product_2.jpg (Foto angle 45 derajat menonjolkan kedalaman dial)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Spesifikasi LIGE Jam Tangan Sport Dual Display:\n\n- Dual Display: Jarum analog kuarsa + layar LED digital\n- Water Resistant aman untuk aktivitas outdoor harian\n- Chronograph aktif: Stopwatch, alarm, tanggal & hari\n- Lampu Backlight LED terang untuk navigasi malam\n- Material bodi tebal dengan strap fleksibel\n\nTampil solid dan percaya diri di segala aktivitas harian.\nLink Shopee resmi: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganPria #JamSport #JamCowok #GayaPria #OOTDPria",
                        "visual_note": "Carousel Slide 2: sprint27_product_11.jpg foto detail lampu LED menyala di kondisi gelap"
                    }
                }
            }
        },
        {
            "angle_id": "angle-03",
            "angle_name": "Satu Jam Serbaguna: Dari Kantor Santai Sampai Sunmori",
            "angle_description": "Menyasar pria praktis yang mencari satu jam tangan serbaguna yang fleksibel digunakan untuk bekerja, gym, lari pagi, hingga nongkrong dan sunmori.",
            "emotional_hook": "Rasa repot gonta-ganti jam tangan untuk urusan berbeda. Membutuhkan satu jam yang menyatukan fungsi olahraga dengan tampilan maskulin yang layak diajak nongkrong.",
            "posts": {
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Paling malas kalau harus punya jam beda-beda buat tiap urusan kecil. ⏱️\n\nMau olahraga harus ganti jam digital, pas ngantor ganti jam jarum, pas riding ganti lagi yang karet.\n\nSolusi paling praktis emang jam dual display yang memadukan dial jarum klasik sama layar digital aktif dalam satu bodi sporty.",
                        "visual_note": "Foto sprint27_product_4.jpg: Jam tangan LIGE dipakai di pergelangan tangan fleksibel"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi fitur all-in-one LIGE Jam Dual Display:\n\n- Dial Analog + LED: Tampilan formal sekaligus fungsional\n- Strap silikon elastis: Anti gerah & keringat pas olahraga\n- Fitur Chrono & Timer: Pas buat ngukur waktu workout/gym\n- Water resistant: Aman dipakai di segala cuaca\n- Konstruksi kokoh: Awet untuk penggunaan jangka panjang\n\nSolusi praktis sat-set tiap hari.\nLink Shopee resmi: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganCowok #OOTDPria #JamSportPria #GayaPria",
                        "visual_note": "Foto sprint27_product_5.jpg: Tampilan strap silikon dan penampang belakang jam"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Pernah merasa ribet karena pergelangan tangan harus sering gonta-ganti jam sesuai agenda?\n\nPagi butuh stopwatch buat jogging, siang butuh tampilan jarum rapi buat kerja santai, sore butuh jam tahan air buat riding balik ke rumah.\n\nKonsep dual display hadir untuk menjawab kebutuhan itu: menyatukan kepraktisan stopwatch digital dengan keanggunan jarum analog dalam satu jam serbaguna.",
                        "visual_note": "Foto kolase sprint27_product_12.jpg dan sprint27_product_13.jpg: Tampilan jam di berbagai situasi"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi fitur all-in-one LIGE Jam Tangan Pria Dual Display:\n\n- Fleksibilitas Waktu Ganda: Menampilkan zona waktu analog dan digital secara harmonis\n- Fitur Produktivitas & Olahraga: Stopwatch milidetik untuk latihan fisik, alarm pengingat jam kerja, dan penanggalan harian\n- Perlindungan Tahan Air: Bebas khawatir terhadap guyuran hujan di perjalanan atau percikan air saat wudhu/cuci tangan\n- Material Nyaman: Tali pengikat karet lembut yang tidak menyerap keringat dan mudah dibersihkan\n- Tampilan Malam Terang: Backlight LED yang memudahkan melihat waktu saat berkendara malam\n\nSatu jam tangan untuk memenuhi berbagai kebutuhan harian pria aktif.\nLink pembelian Shopee: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganPria #JamTanganSport #AksesorisPria #GayaHidupPria #JamOlahraga",
                        "visual_note": "Foto sprint27_product_14.jpg: Fitur dual display menyala lengkap dengan informasi waktu"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Satu jam buat semua agenda harian: ngantor santai, workout gym, sampai sunmori bareng teman. ⏱️\n\nGak perlu bingung gonta-ganti jam tangan. Perpaduan jarum analog klasik dan layar digital LED bikin tampilannya fleksibel di segala situasi.\n\nCek slide berikutnya untuk detail fitur dan materialnya. 👉",
                        "visual_note": "Carousel Slide 1: sprint27_product_4.jpg (Jam tangan dalam setting aktivitas dinamis)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Fitur unggulan LIGE Dual Display Sport Watch:\n\n- Analog Quartz + Digital LED multifungsi\n- Stopwatch & alarm harian terintegrasi\n- Water Resistant untuk cuaca hujan & aktivitas basah\n- Strap silikon elastis anti lembab & nyaman\n- LED Backlight terang untuk kondisi gelap\n\nPilihan tepat jam tangan praktis dan fungsional.\nLink belanja Shopee: https://s.shopee.co.id/2BFO1kXcTq\n\n#JamTanganCowok #JamTanganKeren #AksesorisPria #JamTactical #JamSport",
                        "visual_note": "Carousel Slide 2: sprint27_product_12.jpg foto detail dial dan ergonomi tali jam"
                    }
                }
            }
        }
    ]

    data["campaign_strategy"] = campaign_strategy

    data["campaign"] = {
        "campaign_id": "T-2702",
        "campaign_name": "LIGE Dual Display Tactical Watch Viral Threads & Omnichannel Campaign",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_audience": campaign_strategy["target_audience"],
        "material_spec_summary": {
            "movement": "Dual Movement (Analog Quartz Movement + Digital LED Electronic Module)",
            "key_properties": [
                "Dual Display Synchronized: Menampilkan waktu ganda analog dan digital secara presisi untuk efisiensi pandang",
                "Water Resistant: Ketahanan terhadap cipratan air harian, hujan gerimis hingga lebat saat berkendara, dan keringat",
                "Chronograph & Multi-function: Stopwatch presisi, alarm harian, dan kalender otomatis hari & tanggal",
                "Illumination: Jarum luminer fosfor dan lampu latar LED backlight untuk visibilitas malam hari",
                "Rugged Bezel & Case: Desain bezel kokoh dengan gaya tactical militer modern yang melindungi kaca jam dari benturan harian",
                "Comfort Strap: Tali karet silikon elastis yang tahan keringat, mudah dibersihkan, dan tidak licin saat basah"
            ],
            "positioning": "Jam tangan sport tactical multi-fungsi tangguh dan berpenampilan maskulin dengan harga sangat terjangkau bagi pria aktif yang butuh durabilitas harian."
        },
        "copywriting_angles": copywriting_angles,
        "platform_strategy": {
            "threads": {
                "primary_focus": "Diskusi santai seputar dilema pria (jam kemasukan air saat riding, saltum jam rapuh, kepraktisan dual display), observasi relatable, punchline di kalimat pertama",
                "format": "2-Post Thread Split (Post 1: Situational Hook -> Post 2: Curated Specs + link Shopee)",
                "recommended_posting_hours_wib": [
                    "07:30-09:00",
                    "12:00-13:30",
                    "19:00-21:30"
                ]
            },
            "facebook": {
                "primary_focus": "Storytelling observatif komuter/riding, listicle ringkas fungsi teknis, nada bersahabat dan informatif",
                "format": "Post 1 naratif relatable + Post 2 kurasi spek lengkap + link Shopee di badan postingan",
                "recommended_posting_hours_wib": [
                    "08:00-10:00",
                    "13:00-15:00",
                    "19:30-21:00"
                ]
            },
            "instagram": {
                "primary_focus": "Visual showcase dial gahar & gaya tactical sporty, micro-blogging carousel, punchy caption",
                "format": "Carousel multi-slide + caption kurasi ringkas, CTA mengarahkan ke link bio/Shopee",
                "recommended_posting_hours_wib": [
                    "11:30-13:00",
                    "17:30-19:00",
                    "20:00-22:00"
                ]
            }
        }
    }

    # Validation of Threads character limits and hashtag counts
    print("--- VALIDATION REPORT ---")
    all_valid = True
    for a in copywriting_angles:
        angle_id = a["angle_id"]
        for p_name in ["post_1", "post_2"]:
            p = a["posts"]["threads"][p_name]
            caption = p["caption"]
            char_count = len(caption)
            print(f"[{angle_id}][threads][{p_name}] length: {char_count} chars")
            if char_count > 500:
                print(f"  ERROR: Exceeds 500 chars limit! ({char_count} chars)")
                all_valid = False
            
            # Check personal claim violations
            lower_cap = caption.lower()
            forbidden = ["aku sudah pakai", "aku udah pake", "saya sudah pakai", "saya udah pake", "beneran tahan di tangan aku"]
            for f_word in forbidden:
                if f_word in lower_cap:
                    print(f"  ERROR: Prohibited personal claim found: '{f_word}'")
                    all_valid = False

            if p_name == "post_2":
                if affiliate_url not in caption:
                    print("  ERROR: Affiliate URL missing from post_2!")
                    all_valid = False
                # Check hashtag count
                tags = [w for w in caption.split() if w.startswith("#")]
                print(f"  Hashtag count: {len(tags)} ({tags})")
                if not (3 <= len(tags) <= 5):
                    print(f"  ERROR: Hashtag count {len(tags)} not between 3 and 5!")
                    all_valid = False

    if not all_valid:
        raise ValueError("Validation failed! Please fix issues before saving.")

    with open("docs/sprint27_campaign.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully updated docs/sprint27_campaign.json!")

if __name__ == "__main__":
    generate_sprint27_data()
