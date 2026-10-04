#!/usr/bin/env python3
"""
Tool to enrich docs/sprint29_campaign.json with Threads viral strategy,
copywriting angles, specifications, and platform strategies compliant with Gathot standards.
Product: Homedoki Rak Piring Wastafel Dapur Stainless Steel Multi-fungsi Dengan Penutup
Affiliate Link: https://s.shopee.co.id/8AWbWHUOPx
"""
import json
import re
from datetime import datetime, timezone

def generate_sprint29_data():
    with open("docs/sprint29_campaign.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    affiliate_url = "https://s.shopee.co.id/8AWbWHUOPx"

    data["product_id"] = "homedoki-rak-piring-wastafel-penutup"
    data["product_name"] = "Homedoki Rak Piring Wastafel Dapur Stainless Steel Multi-fungsi Dengan Penutup"
    data["status"] = "ready_for_campaign"
    data["affiliate_url"] = affiliate_url
    data["category"] = "Perlengkapan Rumah / Peralatan Dapur / Rak Dapur"

    data["specs"] = [
        "Desain Over-The-Sink: Terpasang tepat di atas bak wastafel sehingga air cucian langsung mengalir ke saluran pembuangan tanpa mengotori meja counter",
        "Pintu Penutup Higienis: Dilengkapi penutup pintu model flip untuk melindungi piring dan peralatan makan dari debu, kotoran, lalat, dan serangga dapur",
        "Material Stainless Steel Tebal: Konstruksi baja tahan karat yang kokoh, stabil menahan beban perabot makan, serta tahan karat di lingkungan lembap",
        "Kompartemen Terorganisir: Rak piring, rak mangkok, wadah sendok garpu bersekat, slot pisau aman, gantungan centong/spatula, dan rak sabun/spons",
        "Pilihan Dimensi Beragam: Tersedia ukuran lebar 65 cm, 75 cm, 85 cm, 95 cm, hingga 105 cm (struktur 2 tingkat) yang dapat disesuaikan dengan ukuran wastafel",
        "Solusi Dapur Rapi & Hemat Ruang: Memaksimalkan area vertikal yang sering tidak terpakai, ideal untuk dapur minimalis, apartemen, maupun rumah modern"
    ]

    data["campaign_strategy"] = {
        "target_audience": "Pasangan muda, pemilik hunian minimalis atau apartemen, serta ibu rumah tangga modern usia 22-45 tahun yang menginginkan area dapur bersih, higienis, dan bebas genangan air sehabis mencuci piring.",
        "key_selling_points": [
            "Desain di atas wastafel mengalirkan tetesan air langsung ke bak cuci, menjaga meja counter tetap kering",
            "Pintu penutup model flip melindungi peralatan makan dari debu, kotoran, dan serangga dapur",
            "Rangka baja tahan karat (stainless steel) tebal yang kuat, awet, dan anti korosi",
            "Kompartemen all-in-one menampung piring, mangkok, sendok, pisau, dan perlengkapan cuci dalam satu tempat",
            "Estetika modern minimalis dengan pilihan warna hitam dan putih yang serasi untuk dapur masa kini"
        ],
        "threads_viral_strategy": {
            "compliance": "Sesuai standar Gathot: Tanpa klaim konsumsi pribadi palsu ('aku/saya sudah pakai'), tanpa emoji berlebihan, karakter Threads <= 500 per post, link affiliate resmi Shopee, hashtag terarah 3-5 tags.",
            "core_narrative": "Mengangkat dilema harian meja dapur yang becek dan berantakan sehabis cuci piring, membedah pentingnya proteksi higienis rak piring tertutup, serta menyajikan kurasi objektif rak wastafel Homedoki berbahan stainless steel.",
            "framework": "2-Post Thread Split (Post 1: Situational Hook / Dilemma -> Post 2: Curated Specs & Soft CTA Shopee)"
        }
    }

    data["campaign"] = {
        "campaign_id": "sprint29-homedoki-rak-piring-wastafel",
        "campaign_name": "Kurasi Santai & Emosional Homedoki Rak Piring Wastafel Dapur Stainless Steel",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_audience": {
            "demographics": "Pria & wanita usia 22-45 tahun, pasangan baru menikah, penghuni rumah minimalis atau apartemen tipe studio/2BR, serta siapa saja yang aktif memasak di dapur dengan luas terbatas.",
            "pain_points": [
                "Meja counter dapur selalu basah dan becek karena air tirisan piring meluber ke mana-mana",
                "Piring dan mangkok di rak terbuka rawan terpapar debu, lalat, atau serangga sehingga harus dicuci ulang sebelum makan",
                "Alat masak, pisau, sendok, dan talenan tercecer tanpa tempat khusus sehingga dapur terasa sesak dan berantakan",
                "Area vertikal di atas wastafel dibiarkan kosong padahal luas meja dapur sangat terbatas"
            ],
            "tone_and_manner": "Santai, solutif, observant, memvalidasi kerepotan harian di dapur, kurasi objektif berbasis spesifikasi teknis, tanpa klaim pemakaian palsu."
        },
        "copywriting_angles": [
            {
                "angle_id": "angle-01",
                "angle_name": "Dilema Meja Dapur Selalu Becek & Sumpek Sehabis Cuci Piring",
                "target_trigger": "Relatable pain point meja counter basah dan ruang dapur mungil yang terasa sesak",
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Dilema klasik sehabis beres-beres dapur: piring sudah dicuci bersih, tapi meja counter malah basah becek karena air tirisan meluber ke mana-mana.\n\nTumpukan cucian juga bikin dapur mungil makin terasa sumpek. Padahal solusinya bukan menambah luas meja, melainkan memanfaatkan ruang vertikal di atas wastafel supaya air tirisan langsung jatuh ke saluran pembuangan.",
                        "visual_note": "Foto sprint29_product_1.jpg: Tampilan rak piring wastafel Homedoki dengan pintu penutup di atas sink dapur"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi rak wastafel Homedoki ini bisa jadi solusi dapur yang rapi:\n\n• Desain over-the-sink: air tirisan langsung ke bak cuci, meja tetap kering\n• Pintu penutup: piring aman dari debu & serangga dapur\n• Struktur stainless steel tebal dan anti karat\n• Kompartemen lengkap untuk piring, mangkok, pisau, dan spons\n\nCek spesifikasi dan variasi ukurannya di Shopee:\nhttps://s.shopee.co.id/8AWbWHUOPx\n\n#DapurMinimalis #RakPiring #Homedoki #OrganisasiDapur #ShopeeHaul",
                        "visual_note": "Foto sprint29_product_2.jpg: Detail kompartemen dan konstruksi stainless steel rak wastafel Homedoki"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Bagi yang sering beraktivitas di dapur compact atau apartemen, masalah paling umum biasanya bukan pada cucian piringnya, melainkan meja wastafel yang cepat becek sehabis dipakai.\n\nAir sisa tirisan yang menggenang sering kali membuat lap meja basah kuyup dan area dapur terlihat kurang tertata. Pemanfaatan ruang vertikal di atas wastafel merupakan pendekatan cerdas untuk menghemat space sekaligus menjaga kebersihan meja dapur secara alami.",
                        "visual_note": "Foto sprint29_product_1.jpg: Overview rak wastafel Homedoki di area dapur"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Spesifikasi unggulan Homedoki Rak Wastafel Stainless Steel Berpenutup:\n\n1. Desain Over-The-Sink: Drainase gravitasi otomatis langsung ke bak wastafel tanpa nampan tambahan.\n2. Pintu Penutup Flip: Menjaga peralatan makan tetap bersih dan terhindar dari debu maupun serangga.\n3. Material Baja Tahan Karat: Kokoh, tahan beban tumpukan piring, dan anti korosi.\n4. Kompartemen Komprehensif: Wadah piring, mangkok, tempat pisau higienis, rak talenan, serta keranjang spons.\n\nPilihan tepat untuk dapur yang lebih higienis dan terorganisir.\nTersedia di official store Shopee:\nhttps://s.shopee.co.id/8AWbWHUOPx\n\n#DapurMinimalis #RakPiringWastafel #Homedoki #KitchenOrganization #ShopeeFinds",
                        "visual_note": "Foto sprint29_product_3.jpg: Kapasitas penyimpanan piring dan peralatan dapur pada rak Homedoki"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Dapur rapi dan meja counter kering berawal dari penataan ruang yang cermat. ✨\n\nTidak perlu meja dapur yang luas untuk mendapatkan area cuci piring yang bersih dan estetik.\n\nGeser ke samping untuk melihat detail spesifikasi dan kompartemen rak wastafel berpenutup. 👉",
                        "visual_note": "Carousel Slide 1: sprint29_product_1.jpg (Tampilan estetik rak wastafel Homedoki)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Keunggulan Homedoki Rak Piring Wastafel Stainless Steel:\n\n- Desain over-the-sink bebas becek di meja dapur\n- Pintu penutup transparan higienis anti debu\n- Rangka stainless steel tebal dan stabil\n- Kompartemen multi-fungsi untuk piring, mangkok, dan pisau\n- Pilihan warna hitam & putih modern\n\nTemukan ukuran yang pas untuk dapurmu di Shopee.\nLink produk: https://s.shopee.co.id/8AWbWHUOPx\n\n#DapurMinimalis #RakPiring #InspirasiDapur #Homedoki #ShopeeID",
                        "visual_note": "Carousel Slide 2: sprint29_product_4.jpg (Detail fitur dan kompartemen rak)"
                    }
                }
            },
            {
                "angle_id": "angle-02",
                "angle_name": "Proteksi Piring Bersih dari Debu & Serangga dengan Rak Tertutup",
                "target_trigger": "Fokus higienitas dan kepraktisan tanpa harus membilas piring dua kali",
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Pernah merasa ragu saat mau mengambil piring di rak terbuka karena takut sudah terpapar debu halus atau lalat dapur? Ujung-ujungnya harus dibilas ulang sebelum dipakai makan.\n\nKekhawatiran higienitas seperti ini memang wajar di dapur terbuka. Itulah sebabnya rak piring dengan pintu penutup mulai banyak dilirik untuk perlindungan ekstra bagi perabot makan harian.",
                        "visual_note": "Foto sprint29_product_2.jpg: Tampilan pintu penutup rak wastafel Homedoki yang higienis"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Homedoki menghadirkan rak wastafel dengan proteksi pintu penutup:\n\n• Pintu penutup model flip menjaga piring tetap higienis dan terbebas dari serangga\n• Konstruksi baja tahan karat (stainless steel) yang kokoh dan awet\n• Slot piring dan mangkok berkapasitas besar dengan tirisan langsung ke wastafel\n• Tersedia opsi ukuran lebar 65 cm hingga 105 cm\n\nCek promo dan ulasan produknya di Shopee:\nhttps://s.shopee.co.id/8AWbWHUOPx\n\n#DapurBersih #RakPiringHigienis #Homedoki #PeralatanDapur #ShopeeID",
                        "visual_note": "Foto sprint29_product_5.jpg: Struktur penutup dan susunan piring pada rak wastafel Homedoki"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Menjaga peralatan makan tetap bersih setelah dicuci adalah tantangan tersendiri, terutama bagi rumah dengan ventilasi dapur aktif atau konsep open kitchen.\n\nRak piring terbuka sering kali mengundang debu melayang atau serangga hinggap tanpa disadari. Menggunakan rak tirisan yang dilengkapi penutup merupakan alternatif praktis agar peralatan makan selalu siap pakai tanpa perlu dibilas berulang kali.",
                        "visual_note": "Foto sprint29_product_2.jpg: Proteksi higienis pintu rak wastafel Homedoki"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Fitur higienis Homedoki Rak Wastafel Penutup:\n\n1. Pintu Tertutup: Melindungi perabot dari debu, serangga, dan percikan minyak masakan.\n2. Aliran Air Efisien: Tetesan air cucian langsung jatuh ke wastafel sehingga rak tetap kering dan tidak lembap.\n3. Rangka Stainless Steel: Tahan korosi air cuci dan mudah dibersihkan.\n4. Rak Multi-tier: Muat puluhan piring, mangkok, serta wadah sendok garpu tertata rapi.\n\nInvestasi praktis untuk menjaga kesehatan dan kebersihan perabot rumah tangga.\nKunjungi tautan resmi Shopee:\nhttps://s.shopee.co.id/8AWbWHUOPx\n\n#DapurBersih #RakPiringHigienis #Homedoki #PeralatanRumah #BelanjaShopee",
                        "visual_note": "Foto sprint29_product_6.jpg: Dimensi dan kapasitas rak piring Homedoki"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Piring bersih bebas debu dan serangga, siap pakai kapan saja untuk keluarga tercinta. 🍽️✨\n\nPerlindungan higienis pada area tirisan piring membantu menjaga kebersihan makanan tetap optimal.\n\nSimak kurasi fitur rak wastafel berpenutup pada slide berikutnya. 👉",
                        "visual_note": "Carousel Slide 1: sprint29_product_2.jpg (Fokus proteksi higienis rak penutup)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Keunggulan Proteksi Higienis Rak Homedoki:\n\n- Pintu flip penutup anti debu dan serangga\n- Tetesan cucian langsung ke wastafel, bebas jamur lembap\n- Bahan stainless steel food-grade yang tahan lama\n- Kapasitas lega untuk piring, mangkok, dan sendok\n\nPastikan peralatan makan keluarga selalu higienis.\nLink produk di Shopee: https://s.shopee.co.id/8AWbWHUOPx\n\n#RakPiring #DapurHigienis #Homedoki #RumahMinimalis #ShopeePromo",
                        "visual_note": "Carousel Slide 2: sprint29_product_5.jpg (Detail pintu penutup dan rak)"
                    }
                }
            },
            {
                "angle_id": "angle-03",
                "angle_name": "Seni Memanfaatkan Dead Space Dapur Supaya Estetik & Teratur",
                "target_trigger": "Optimalisasi ruang vertikal dan estetika dapur apartemen/rumah compact",
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Ruang kosong tepat di atas wastafel sering kali jadi 'dead space' yang terabaikan. Sementara itu, meja dapur penuh sesak oleh botol sabun, talenan, dan piring basah.\n\nDengan memanfaatkan rak vertikal di atas wastafel, semua kebutuhan cuci piring bisa terkonsentrasi di satu titik tanpa memakan tempat di meja dapur sedikit pun.",
                        "visual_note": "Foto sprint29_product_3.jpg: Pemanfaatan ruang vertikal di atas sink dengan rak Homedoki"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi rak wastafel multifungsi Homedoki untuk efisiensi ruang:\n\n• Memaksimalkan area vertikal dengan susunan 2 tingkat yang kokoh\n• Wadah terpadu untuk talenan, pisau, spatula, dan sabun cuci\n• Pintu penutup transparan memberi kesan modern dan rapi\n• Material stainless steel tahan beban berat dan anti karat\n\nCek pilihan ukuran dan modelnya di Shopee:\nhttps://s.shopee.co.id/8AWbWHUOPx\n\n#DapurEstetik #InspirasiDapur #Homedoki #RakWastafel #ShopeePromo",
                        "visual_note": "Foto sprint29_product_7.jpg: Kompartemen terpadu dan akses mudah pada rak wastafel Homedoki"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Memiliki dapur berukuran ringkas bukan berarti harus berkompromi dengan kerapian. Sering kali rasa sempit itu timbul karena barang-barang diletakkan secara horizontal di atas meja dapur.\n\nMemanfaatkan dinding dan area vertikal di atas bak wastafel adalah trik penataan ruang yang banyak diterapkan pada hunian modern untuk menciptakan ilusi dapur yang lebih luas dan lapang.",
                        "visual_note": "Foto sprint29_product_3.jpg: Inspirasi penataan dapur compact dengan rak wastafel"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Efisiensi ruang dapur bersama Homedoki Rak Wastafel Stainless Steel:\n\n1. Solusi Vertikal Pintar: Mengubah area kosong di atas sink menjadi ruang penyimpanan multifungsi.\n2. Penataan Rapi: Tempat khusus untuk piring, mangkok, sendok, pisau, dan talenan dalam satu jangkauan tangan.\n3. Pintu Tertutup: Memberikan tampilan dapur yang rapi dan terorganisir tanpa kesan perabotan bertumpuk.\n4. Bahan Stainless Berkualitas: Kokoh dan tidak mudah goyah saat memuat banyak perabot.\n\nTingkatkan kenyamanan dapur rumah Anda.\nLink pembelian resmi di Shopee:\nhttps://s.shopee.co.id/8AWbWHUOPx\n\n#DapurRapi #OrganisasiRumah #Homedoki #PeralatanDapur #BelanjaShopee",
                        "visual_note": "Foto sprint29_product_8.jpg: Ilustrasi kompartemen dan kestabilan rak Homedoki"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Ubah sudut dapur mungil jadi lebih tertata dan estetik dengan pemanfaatan ruang vertikal. 🌿✨\n\nSemua perlengkapan cuci piring tersusun rapi dalam satu jangkauan tanpa bikin meja dapur penuh sesak.\n\nGeser untuk melihat keunggulan kompartemen rak multifungsi ini. 👉",
                        "visual_note": "Carousel Slide 1: sprint29_product_3.jpg (Tampilan dapur rapi dengan rak wastafel)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Highlight Homedoki Rak Wastafel Multifungsi:\n\n- Pemanfaatan area vertikal di atas wastafel\n- Kompartemen lengkap: piring, mangkok, pisau & talenan\n- Pintu penutup elegan untuk estetika dapur modern\n- Rangka stainless steel tebal dan anti korosi\n\nWujudkan dapur idaman yang rapi dan bersih.\nLink produk di Shopee: https://s.shopee.co.id/8AWbWHUOPx\n\n#DapurEstetik #InspirasiDapur #Homedoki #KitchenHacks #ShopeeID",
                        "visual_note": "Carousel Slide 2: sprint29_product_7.jpg (Detail kapasitas rak piring)"
                    }
                }
            }
        ],
        "material_spec_summary": {
            "product_highlight": "Homedoki Rak Piring Wastafel Dapur Stainless Steel Multi-fungsi Dengan Penutup",
            "key_properties": [
                "Bahan: Stainless Steel berkualitas tinggi, tahan karat dan kokoh menopang beban berat",
                "Fitur Penutup: Pintu flip model tertutup melindungi perabot makan dari debu dapur, lalat, dan cipratan kotoran",
                "Sistem Tirisan Over-the-Sink: Air cucian piring langsung menetes ke bak cuci tanpa menggenang di meja dapur",
                "Kelengkapan Kompartemen: Rak piring, rak mangkok, tempat pisau, wadah sendok garpu, gantungan alat masak, serta keranjang spons/sabun",
                "Opsi Dimensi: Panjang 65 cm, 75 cm, 85 cm, 95 cm, hingga 105 cm dengan struktur 2 tingkat (2 Layer)"
            ]
        },
        "platform_strategy": {
            "threads": {
                "primary_focus": "Diskusi teks tajam seputar dilema meja dapur becek, efisiensi ruang compact, dan higienitas rak berpenutup",
                "format": "Thread Split: Post 1 situasi relatable/hook dilema + Post 2 kurasi spesifikasi objektif dan link affiliate Shopee",
                "character_limit": 500,
                "hashtag_policy": "3-5 hashtag relevan per post",
                "recommended_posting_hours_wib": [
                    "07:30-09:00",
                    "12:00-13:30",
                    "19:00-21:30"
                ]
            },
            "facebook": {
                "primary_focus": "Artikel naratif edukatif seputar penataan dapur higienis dan efisiensi ruang rumah minimalis",
                "format": "Post 1 naratif relatable + Post 2 kurasi spek lengkap + link Shopee di badan postingan",
                "recommended_posting_hours_wib": [
                    "08:00-10:00",
                    "13:00-15:00",
                    "19:30-21:00"
                ]
            },
            "instagram": {
                "primary_focus": "Visual showcase rak wastafel estetik, micro-blogging carousel, punchy caption",
                "format": "Carousel multi-slide + caption kurasi ringkas, CTA mengarahkan ke link bio/Shopee",
                "recommended_posting_hours_wib": [
                    "11:30-13:00",
                    "17:30-19:00",
                    "20:00-22:00"
                ]
            }
        }
    }

    # Strict Validation
    forbidden_terms = [
        r"\baku\s+(sudah|udah|pernah|pake|pakai|coba|beli)\b",
        r"\bsaya\s+(sudah|udah|pernah|pake|pakai|coba|beli)\b",
        r"\bpiring\s+aku\b",
        r"\bdapur\s+aku\b",
        r"\brumah\s+aku\b",
        r"\bdi\s+dapurku\b",
        r"\bdi\s+rumahku\b"
    ]

    all_valid = True
    print("--- VALIDATION PROCESS ---")
    for angle in data["campaign"]["copywriting_angles"]:
        print(f"\nChecking angle: {angle['angle_id']} ({angle['angle_name']})")
        for platform in ["threads", "facebook", "instagram"]:
            for post_key in ["post_1", "post_2"]:
                post_data = angle[platform][post_key]
                caption = post_data["caption"]
                char_len = len(caption)

                # Check forbidden terms
                for pattern in forbidden_terms:
                    if re.search(pattern, caption, re.IGNORECASE):
                        print(f"  ERROR: Forbidden personal usage claim pattern '{pattern}' found in {platform} {post_key}!")
                        all_valid = False

                # Threads specific checks
                if platform == "threads":
                    if char_len > 500:
                        print(f"  ERROR: Threads {post_key} exceeds 500 chars (len={char_len})!")
                        all_valid = False
                    else:
                        print(f"  Threads {post_key} length OK: {char_len}/500 chars")

                    if post_key == "post_2":
                        if affiliate_url not in caption:
                            print(f"  ERROR: Affiliate URL missing in Threads post_2!")
                            all_valid = False
                        tags = re.findall(r"#[A-Za-z0-9_]+", caption)
                        if not (3 <= len(tags) <= 5):
                            print(f"  ERROR: Hashtag count {len(tags)} not between 3 and 5 in Threads post_2!")
                            all_valid = False
                        else:
                            print(f"  Hashtags count OK: {len(tags)} tags ({tags})")

                # General post_2 link check
                if post_key == "post_2":
                    if affiliate_url not in caption:
                        print(f"  ERROR: Affiliate URL missing in {platform} post_2!")
                        all_valid = False
                    tags = re.findall(r"#[A-Za-z0-9_]+", caption)
                    if not (3 <= len(tags) <= 5):
                        print(f"  ERROR: Hashtag count {len(tags)} not between 3 and 5 in {platform} {post_key}!")
                        all_valid = False

    if not all_valid:
        raise ValueError("Validation failed! Please fix issues before saving.")

    with open("docs/sprint29_campaign.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("\nSuccessfully updated docs/sprint29_campaign.json!")

if __name__ == "__main__":
    generate_sprint29_data()
