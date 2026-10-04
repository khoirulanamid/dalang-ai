"""Sprint 26 Copywriting Campaign Generator for One Set 4in1 Simple Vest Cherish.

Generates structured copywriting angles adhering strictly to gathot_social_standards.md:
- No personal usage claims ('aku/saya sudah pakai')
- Relatable humor and everyday dilemma hooks
- 2-post thread split (Post 1: hook/pain point, Post 2: specs curation + CTA Shopee link)
- 3-5 focused hashtags
- Thread post length <= 500 characters
- CTA affiliate link: https://s.shopee.co.id/6L4wk65TN6
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def generate_sprint26_campaign():
    campaign_file = Path("docs/sprint26_campaign.json")
    if not campaign_file.exists():
        raise FileNotFoundError(f"{campaign_file} not found")

    with open(campaign_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    affiliate_url = "https://s.shopee.co.id/6L4wk65TN6"
    now_iso = datetime.now(timezone.utc).isoformat()

    specs = [
        "Set komplit 4-in-1: Vest Cherish (outer rompi), Inner manset kaos, Celana cutbray flare, dan Hijab Bella Square",
        "Outer Vest Cherish: Potongan clean-cut minimalis modern, memberi sentuhan layer chic tanpa rasa tebal atau gerah",
        "Inner manset: Serat kain halus lentur dengan sirkulasi udara baik, pas di badan dan nyaman seharian",
        "Celana Cutbray: Pinggang elastis dengan potongan flare di bawah lutut yang memberi efek visual kaki lebih jenjang",
        "Hijab Bella Square: Bahan polycotton warna senada yang lembut, mudah dibentuk, dan tegak rapi di dahi",
        "Konsep Siap Pakai: Seluruh item sudah dirancang selaras warna dan gayanya, menghemat waktu mix and match harian"
    ]

    target_audience = "Mahasiswi, first-jobber, dan cewek hijab muda yang butuh outfit praktis siap pakai (Korean chic modest look) tanpa pusing mix and match tiap pagi"

    campaign_strategy = {
        "target_audience": target_audience,
        "key_selling_points": [
            "Paket komplit 4-in-1 sekali checkout: Vest Cherish, Inner manset, Celana cutbray, dan Hijab Bella Square",
            "Potongan celana cutbray memberi efek visual kaki lebih jenjang dan siluet tubuh lebih proporsional",
            "Solusi praktis siap pakai untuk mengatasi dilema berdiri lama di depan lemari baju tiap pagi",
            "Material nyaman dan adem untuk aktivitas ngampus, kerja santai, hingga nongkrong di iklim tropis",
            "Hemat waktu styling dan hemat budget dibanding belanja 4 item secara eceran terpisah"
        ],
        "threads_viral_strategy": {
            "framework": "2-Post Thread Split (Post 1: Situational Hook / Dilemma -> Post 2: Curated Specs & Soft CTA)",
            "core_narrative": "Menyoroti dilema harian wanita muda yang lelah memilih padanan outfit tiap pagi (wardrobe fatigue), lalu menghadirkan one set 4in1 sebagai kurasi praktis siap pakai",
            "compliance": "Sesuai standar Gathot: Tanpa klaim konsumsi pribadi palsu, tanpa emoji bullets, karakter Threads <= 500 per post, link affiliate resmi Shopee"
        }
    }

    copywriting_angles = [
        {
            "angle_id": "angle-01",
            "angle_name": "Solusi Dilema Baju Ngampus & Nongkrong Sat-Set",
            "angle_description": "Menyasar mahasiswi dan cewek aktif yang sering membuang waktu 20 menit di depan lemari baju hanya untuk mencocokkan outfit harian.",
            "emotional_hook": "Relatable pain point: isi lemari penuh sesak tapi tetap merasa tidak punya baju yang cocok. Solusinya one set terkoordinasi yang langsung siap jalan dalam hitungan detik.",
            "posts": {
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Pernah berdiri 20 menit depan lemari tapi merasa gak punya baju? 👗\n\n"
                            "Lemari penuh sesak, tapi tiap mau ngampus atau nongkrong bingung setengah mati "
                            "mencocokkan atasan, bawahan, dan hijab. Ujung-ujungnya berangkat telat.\n\n"
                            "Kuncinya bukan nambah tumpukan baju acak, tapi punya setelan siap pakai yang "
                            "potongannya sudah terkurasi rapi dari atas sampai bawah."
                        ),
                        "visual_note": "Foto sprint26_product_1.jpg: Model mengenakan One Set 4in1 Vest Cherish lengkap pose santai outdoor/indoor"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "One Set 4in1 Simple Vest Cherish hadir sebagai solusi outfit praktis:\n\n"
                            "- Vest Cherish: aksen rompi minimalis modern\n"
                            "- Inner manset: bahan adem, lentur, nyaman dipakai seharian\n"
                            "- Celana cutbray: siluet ramping dengan ilusi kaki lebih jenjang\n"
                            "- Hijab Bella Square: warna senada, mudah dibentuk rapi\n\n"
                            "Praktis dipakai tanpa ribet padu padan dari nol.\n"
                            "Link belanja Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#OneSetHijab #OutfitNgampus #OOTDHijab #SetelanWanita #BellaSquare"
                        ),
                        "visual_note": "Foto sprint26_product_2.jpg: Flatlay detail 4 item komplit (vest, inner, cutbray, hijab) memperlihatkan keharmonisan warna"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Dilema klasik setiap pagi: lemari baju penuh tapi pas mau berangkat kuliah atau kerja, rasanya nggak ada satu pun baju yang pas dipadukan.\n\n"
                            "Akhirnya baju berserakan di kasur cuma gara-gara bingung mencocokkan warna atasan sama kerudung yang senada.\n\n"
                            "Padahal punya outfit siap pakai yang sudah terkoordinasi rapi bikin rutinitas pagi jauh lebih tenang dan hemat waktu."
                        ),
                        "visual_note": "Foto kolase sprint26_product_1.jpg dan sprint26_product_3.jpg: Tampilan utuh setelan saat dikenakan model"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "Buat yang butuh outfit rapi tanpa ribet mix and match, One Set 4in1 Simple Vest Cherish ini menyajikan paket komplit:\n\n"
                            "- Vest Cherish: rompi simpel potongan kekinian\n"
                            "- Inner Manset: bahan lentur dan sejuk di badan\n"
                            "- Celana Cutbray: siluet flare yang memberi efek kaki lebih jenjang\n"
                            "- Hijab Bella Square: polycotton warna senada yang mudah dibentuk\n\n"
                            "Satu paket lengkap langsung siap pakai untuk daily outfit.\n"
                            "Link belanja resmi Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#OneSetWanita #OOTDHijabIndo #OutfitKuliahSimpel"
                        ),
                        "visual_note": "Foto sprint26_product_4.jpg: Detail bahan vest dan jahitan celana cutbray"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Outfit sat-set anti drama lemari penuh tapi gak ada baju. ✨\n\n"
                            "Pernah ngitung berapa menit yang terbuang tiap pagi cuma buat mikir padu padan baju dan hijab yang senada?\n\n"
                            "Swipe ke samping buat lihat kurasi setelan 4-in-1 yang langsung beres dalam satu tarikan hanger ➡️"
                        ),
                        "visual_note": "Carousel Slide 1: Foto sprint26_product_1.jpg - OOTD model full body dengan aesthetic tone"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "Kurasi detail One Set 4in1 Simple Vest Cherish:\n\n"
                            "- Simple Vest Cherish (outer rompi modern)\n"
                            "- Inner manset adem & fleksibel\n"
                            "- Celana cutbray flare (ilusi visual kaki jenjang)\n"
                            "- Hijab Bella Square warna senada\n\n"
                            "Satu set langsung siap pakai tanpa perlu pusing padu padan.\n"
                            "Link belanja tersedia di Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#OneSet4in1 #OOTDHijabStyle #OutfitAesthetic #HijabLook"
                        ),
                        "visual_note": "Carousel Slide 2 & 3: Foto sprint26_product_2.jpg dan sprint26_product_5.jpg detail tekstur dan potongan"
                    }
                }
            }
        },
        {
            "angle_id": "angle-02",
            "angle_name": "Siluet Ramping & Efek Kaki Jenjang (Korean Chic Look)",
            "angle_description": "Menyasar wanita yang menginginkan penampilan layering modis ala Korea tanpa takut badan terlihat tenggelam atau bantet.",
            "emotional_hook": "Keinginan tampil stylish dengan gaya layering vest, tapi khawatir potongan baju membuat siluet tubuh tampak bulky. Kombinasi vest pas pinggang dan celana cutbray memberikan proporsi visual yang jenjang.",
            "posts": {
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Mau layering aesthetic tapi takut kelihatan numpuk dan gerah? 🤔\n\n"
                            "Gaya vest dengan inner lagi digemari buat look rapi ala Korean chic. "
                            "Tapi kalau potongannya terlalu kaku atau celananya salah pilih, siluet badan justru tampak tenggelam.\n\n"
                            "Kombinasi rompi simpel dengan celana flare terbukti efektif menciptakan siluet ramping dan proporsional."
                        ),
                        "visual_note": "Foto sprint26_product_3.jpg: Model memperlihatkan siluet kaki jenjang dengan celana cutbray dan vest cherish"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "Kurasi spesifikasi One Set 4in1 Simple Vest Cherish:\n\n"
                            "- Celana cutbray: flare proporsional, memberi efek kaki jenjang\n"
                            "- Vest Cherish: panjang pas pinggang, bikin postur tegak\n"
                            "- Inner manset: kain halus, adem, dan lentur\n"
                            "- Hijab Bella Square: polycotton lembut, tegak di dahi\n\n"
                            "Tampilan modis siap jalan tanpa pusing styling.\n"
                            "Link belanja Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#KoreanStyleHijab #CelanaCutbray #VestCherish #OOTDHijab #SetelanKekinian"
                        ),
                        "visual_note": "Foto sprint26_product_6.jpg: Close-up potongan pinggang vest dan jatuhnya celana flare"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Layering outfit itu seru, tapi kalau komposisinya salah, badan sering kelihatan lebih pendek atau terlihat penuh.\n\n"
                            "Banyak yang suka gaya rompi atau vest dipadu inner kaos, tapi bingung memilih bawahan yang proporsional.\n\n"
                            "Kuncinya ada pada celana cutbray dengan siluet flare di bawah lutut yang secara visual menyeimbangkan potongan atasan vest."
                        ),
                        "visual_note": "Foto sprint26_product_3.jpg: Tampilan gaya Korean chic modest yang clean"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "One Set 4in1 Vest Cherish dirancang dengan proporsi visual yang pas:\n\n"
                            "- Celana Cutbray: siluet melebar dari lutut ke bawah, memberi efek jenjang maksimal\n"
                            "- Vest Cherish: potongan cropped proporsional agar pinggang terlihat rapi\n"
                            "- Inner Manset: fit di badan tanpa gerah berkat serat kain bernapas\n"
                            "- Bella Square: hijab segiempat senada yang mudah distyling\n\n"
                            "Kombinasi stylish yang langsung proporsional sejak pertama dipakai.\n"
                            "Link pemesanan Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#FashionHijabKekinian #SetelanCutbray #GayaKoreanChic"
                        ),
                        "visual_note": "Foto sprint26_product_7.jpg: Detail bahan dan kelenturan celana cutbray"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Trik simpel bikin ilusi kaki jenjang dengan gaya layering. ✨\n\n"
                            "Rahasia Korean modest look yang rapi: padukan vest berpotongan clean dengan celana cutbray flare.\n\n"
                            "Gak perlu takut gerah atau kelihatan bulky, formulanya pas buat daily hangout.\n\n"
                            "Detail lengkap setelannya ada di slide berikutnya ➡️"
                        ),
                        "visual_note": "Carousel Slide 1: Foto sprint26_product_3.jpg fokus pada full outfit siluet"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "Spesifikasi One Set 4in1 Simple Vest Cherish:\n\n"
                            "- Vest Cherish outer dengan aksen simpel modern\n"
                            "- Inner lengan panjang elastis & adem\n"
                            "- Celana flare cutbray yang memberi efek visual kaki jenjang\n"
                            "- Hijab Bella Square polycotton rapi di dahi\n\n"
                            "Solusi instan buat tampil rapi dan estetik.\n"
                            "Link produk di Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#OOTDIndo #SetelanVest #CelanaCutbrayHijab #KoreanChicHijab"
                        ),
                        "visual_note": "Carousel Slide 2: Foto sprint26_product_6.jpg detail jahitan vest"
                    }
                }
            }
        },
        {
            "angle_id": "angle-03",
            "angle_name": "Paket Komplit 4-in-1: Hemat Waktu & Bebas Repot",
            "angle_description": "Menyasar pembeli cerdas (smart shopper) yang ingin efisiensi maksimal: satu transaksi sudah dapat seluruh kebutuhan outfit tanpa risiko salah padu warna.",
            "emotional_hook": "Kelelahan membeli pakaian secara terpisah (atasan, bawahan, jilbab beda toko) yang sering kali berujung warna tidak matching dan ongkir bertumpuk.",
            "posts": {
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Beli outfit eceran seringnya hijab sama celana gak pernah senada. 😅\n\n"
                            "Paling melelahkan itu beli atasan, bawahan, dan jilbab terpisah. "
                            "Pas barang datang, tone warnanya beda tipis atau siluet potongannya bentrok. "
                            "Belum lagi ongkir jadi berkali-kali lipat.\n\n"
                            "Paket terkoordinasi 4-in-1 memangkas kerepotan belanja sekaligus waktu mikir padu padan tiap pagi."
                        ),
                        "visual_note": "Foto sprint26_product_2.jpg: Flatlay 4 elemen paket terhampar rapi"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "Kurasi detail paket One Set 4in1 Simple Vest Cherish:\n\n"
                            "- 1x Vest Cherish aksen rompi modern\n"
                            "- 1x Inner manset lengan panjang adem\n"
                            "- 1x Celana cutbray flare elastis\n"
                            "- 1x Hijab Bella Square warna serasi\n\n"
                            "Satu paket lengkap langsung dapat 4 potong outfit siap pakai tanpa repot cari pasangannya.\n"
                            "Link belanja Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#OneSetHijab #OutfitHemat #OOTDSimpel #SetelanWanita #HijabStyle"
                        ),
                        "visual_note": "Foto sprint26_product_8.jpg: Detail kemasan dan kartu display paket lengkap"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Pernah ngalamin beli baju, celana, sama hijab di toko online yang berbeda? "
                            "Pas barang sampai dan dicocokkan, warnanya malah saling balap dan gak sinkron.\n\n"
                            "Selain boros ongkir karena belanja terpisah, waktu yang dihabiskan buat mencari pasangan outfit juga lumayan menguras energi.\n\n"
                            "Solusi paling aman untuk gaya sehari-hari adalah memilih paket setelan yang memang sudah dirancang satu tema warna."
                        ),
                        "visual_note": "Foto sprint26_product_2.jpg: Flatlay set lengkap 4-in-1"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "One Set 4in1 Simple Vest Cherish memberi kepraktisan dalam satu paket belanja:\n\n"
                            "- Outer: Vest Cherish clean look\n"
                            "- Inner: Kaos manset nyaman dan breathable\n"
                            "- Bawahan: Celana cutbray berpinggang elastis\n"
                            "- Hijab: Bella Square dengan warna yang dipastikan senada\n\n"
                            "Sekali dapat langsung satu set lengkap tanpa perlu belanja eceran terpisah.\n"
                            "Link Shopee resmi: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#SetelanSiapPakai #BelanjaCerdas #OOTDHijabPraktis"
                        ),
                        "visual_note": "Foto sprint26_product_5.jpg: Foto close up kain dan tekstur serat bahan"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": (
                            "Gak perlu belanja di 3 toko berbeda cuma buat dapetin 1 OOTD matching. 🛍️\n\n"
                            "Satu paket sudah include vest, inner, celana cutbray, sampai hijab Bella Square yang warnanya udah serasi dari pabrik.\n\n"
                            "Swipe ke samping buat lihat kelengkapan paketnya ➡️"
                        ),
                        "visual_note": "Carousel Slide 1: Foto sprint26_product_2.jpg - Flatlay 4 item lengkap"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": (
                            "Isi Paket One Set 4in1 Simple Vest Cherish:\n\n"
                            "- Simple Vest Cherish\n"
                            "- Inner manset lengan panjang\n"
                            "- Celana cutbray pinggang elastis\n"
                            "- Hijab Bella Square polycotton\n\n"
                            "Outfit rapi siap pakai dalam satu checkout.\n"
                            "Link pembelian ada di Shopee: https://s.shopee.co.id/6L4wk65TN6\n\n"
                            "#OneSetLengkap #OOTDHijabModern #OutfitMahasiswi #DailyHijabLook"
                        ),
                        "visual_note": "Carousel Slide 2: Foto sprint26_product_4.jpg detail produk siap pakai"
                    }
                }
            }
        }
    ]

    material_spec_summary = {
        "material": "Vest Cherish + Inner Manset Spandex/Rayon + Celana Cutbray Scuba/Rib + Hijab Bella Square Polycotton",
        "key_properties": [
            "Vest Cherish: Karakter kain bertekstur rapi dan tidak mudah kusut, memberi layer chic tanpa menambah beban panas",
            "Inner Manset: Serat lentur dengan sirkulasi udara baik, menjaga tubuh tetap sejuk sepanjang hari",
            "Celana Cutbray: Pinggang elastis dengan drape kain yang jatuh stabil, menciptakan ilusi visual kaki lebih panjang",
            "Hijab Bella Square: Polycotton bertekstur halus, tidak licin, dan tegak rapi di dahi saat dibentuk",
            "Penyelarasan Warna Senada: Kurasi palet warna monokrom dan earth-tone harmonis yang langsung matching dari jilbab hingga celana"
        ],
        "positioning": "Solusi outfit all-in-one praktis dan terjangkau bagi wanita muda yang mengutamakan kecepatan bersiap tanpa mengorbankan estetika modest modern."
    }

    platform_strategy = {
        "threads": {
            "primary_focus": "Diskusi santai seputar dilema harian wanita muda saat memilih outfit, punchline kuat di baris pertama, tone relatable tanpa klaim pribadi palsu",
            "format": "Thread bersambung 2 post: Post 1 hook relatable / everyday dilemma, Post 2 kurasi spesifikasi teknis 4-in-1 + CTA link Shopee",
            "character_limit": 500,
            "hashtag_strategy": "3-5 hashtag spesifik komunitas fashion muslim & daily OOTD",
            "recommended_posting_hours_wib": [
                "09:00-11:00",
                "15:30-17:00",
                "19:30-21:30"
            ]
        },
        "facebook": {
            "primary_focus": "Artikel naratif & solusi praktis padu padan outfit kuliah/kantor santai bagi wanita aktif",
            "format": "2 post naratif: Post 1 cerita dilema belanja terpisah vs setelan terpadu, Post 2 kurasi 4 item komplit + link Shopee",
            "recommended_posting_hours_wib": [
                "10:00-12:00",
                "16:00-18:00",
                "20:00-21:30"
            ]
        },
        "instagram": {
            "primary_focus": "Visual showcase padu padan 4-in-1 aesthetic, micro-blogging carousel, punchy caption",
            "format": "Carousel multi-slide + caption kurasi ringkas, CTA mengarahkan ke link bio/Shopee",
            "recommended_posting_hours_wib": [
                "11:30-13:00",
                "17:30-19:00",
                "20:30-22:00"
            ]
        }
    }

    campaign_payload = {
        "campaign_id": "T-2602",
        "campaign_name": "One Set 4in1 Simple Vest Cherish Viral Threads & Omnichannel Campaign",
        "generated_at": now_iso,
        "target_audience": target_audience,
        "copywriting_angles": copywriting_angles,
        "material_spec_summary": material_spec_summary,
        "platform_strategy": platform_strategy
    }

    data["status"] = "ready_for_campaign"
    data["affiliate_url"] = affiliate_url
    data["specs"] = specs
    data["campaign_strategy"] = campaign_strategy
    data["campaign"] = campaign_payload

    with open(campaign_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated sprint26 campaign in {campaign_file}")


if __name__ == "__main__":
    generate_sprint26_campaign()
