#!/usr/bin/env python3
"""
Tool to enrich docs/sprint28_campaign.json with Threads viral strategy,
copywriting angles, specifications, and platform strategies compliant with Gathot standards.
Product: AMORA EMWEHA Jaket Crop Wanita
Affiliate Link: https://s.shopee.co.id/20vxzX4Fx0
"""
import json
import re
from datetime import datetime, timezone

def generate_sprint28_data():
    with open("docs/sprint28_campaign.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    affiliate_url = "https://s.shopee.co.id/20vxzX4Fx0"

    data["product_id"] = "amora-emweha-jaket-crop"
    data["product_name"] = "AMORA EMWEHA Jaket Crop Wanita Outer Lengan Panjang Desain Runcing Depan"
    data["status"] = "ready_for_campaign"
    data["affiliate_url"] = affiliate_url
    data["category"] = "Fashion Muslim / Atasan Wanita"

    data["specs"] = [
        "Model Cropped Modern: Potongan fit kekinian yang memberi ilusi proporsi tubuh lebih jenjang dan rapi",
        "Desain Pointed Front: Aksen potongan depan runcing yang edgy, memberi siluet ramping di area pinggang",
        "Kerah Kemeja Klasik: Menghadirkan siluet smart-casual yang rapi, fleksibel untuk padu padan santai maupun formal",
        "Lengan Panjang Belah (Slit Sleeve): Detail bukaan di ujung lengan untuk kebebasan gerak dan kesan modis",
        "Dimensi Presisi: Lingkar Dada 100 cm, Panjang Baju 53 cm, Panjang Lengan 60 cm, Lingkar Ketiak 48 cm, Lebar Bahu 12 cm",
        "Konsep Fair Price EMWEHA: Value-for-money tinggi dengan standar kurasi jahitan rapi dan harga masuk akal"
    ]

    data["campaign_strategy"] = {
        "target_audience": "Wanita muda usia 18-35 tahun (mahasiswi, fresh graduate, pekerja muda, hijabers, dan pecinta modest fashion) yang mencari outer kasual estetik, mudah dipadupadankan, dan nyaman untuk mobilitas harian.",
        "key_selling_points": [
            "Potongan crop depan meruncing (pointed front) yang memberikan ilusi siluet tubuh lebih ramping dan jenjang",
            "Kerah kemeja klasik yang memberi kesan terstruktur dan rapi untuk berbagai suasana",
            "Aksen belahan di pergelangan lengan (slit cuff) yang menambah sentuhan modern dan dinamis",
            "Ukuran proporsional all-size (LD 100 cm, PJ baju 53 cm, PJ lengan 60 cm) yang pas dan tidak bikin 'tenggelam'",
            "Filosofi Fair Price dari EMWEHA: Tampil percaya diri dan modis dengan harga yang tetap ramah di kantong"
        ],
        "threads_viral_strategy": {
            "compliance": "Sesuai standar Gathot: Tanpa klaim konsumsi pribadi palsu ('aku/saya sudah pakai'), tanpa emoji berlebihan, karakter Threads <= 500 per post, link affiliate resmi Shopee, hashtag terarah 3-5 tags.",
            "core_narrative": "Mengangkat dilema harian wanita seputar memilih outfit yang praktis tapi tetap estetik di foto OOTD, membedah keunggulan teknis cutting pointed front, serta menyajikan kurasi objektif jaket crop EMWEHA yang santai dan suportif secara emosional.",
            "framework": "2-Post Thread Split (Post 1: Situational Hook / Dilemma -> Post 2: Curated Specs & Soft CTA Shopee)"
        }
    }

    data["campaign"] = {
        "campaign_id": "sprint28-amora-emweha-jaket-crop",
        "campaign_name": "Kurasi Santai & Emosional Amora EMWEHA Jaket Crop Wanita",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_audience": {
            "demographics": "Wanita usia 18-35 tahun, mahasiswi, first jobber, pengguna hijab maupun modest fashion kasual yang aktif di media sosial.",
            "pain_points": [
                "Buka lemari penuh tapi bingung memilih outer yang langsung bikin tampilan rapi tanpa ribet",
                "Outer crop pasaran sering kali potongannya terlalu kaku atau kurang pas untuk paduan hijab",
                "Potongan baju yang rata sering membuat siluet tubuh terlihat kotak atau tenggelam di foto OOTD",
                "Mencari pakaian berkualitas dengan harga yang wajar dan tidak menguras anggaran bulanan"
            ],
            "tone_and_manner": "Santai, hangat, observant, memvalidasi dilema harian, kurasi objektif berbasis spesifikasi, tanpa overclaiming."
        },
        "copywriting_angles": [
            {
                "angle_id": "angle-01",
                "angle_name": "Dilema Buka Lemari Penuh tapi Merasa Gak Punya Baju",
                "target_trigger": "Observasi relatable dilema harian perempuan saat memilih outfit hangout santai atau kuliah",
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Pemandangan klasik tiap mau keluar rumah: buka lemari pakaian penuh sesak, tapi ujung-ujungnya bengong 15 menit sambil mikir 'kok berasa gak punya baju ya?' 😭\n\nMasalahnya bukan kurang baju, tapi belum nemu outer serbaguna yang tinggal dilempar ke kaos polos atau inner manset langsung auto kelihatan rapi dan niat dandan.",
                        "visual_note": "Foto sprint28_product_1.jpg: Model mengenakan Amora Jaket Crop dengan siluet rapi dan modern"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi Amora Jaket Crop dari EMWEHA ini menarik buat solusi outfit praktis:\n• Potongan depan runcing (pointed front) yang bikin ilusi pinggang lebih proporsional\n• Kerah kemeja klasik, cocok buat kasual sampai semi-formal\n• Aksen slit di ujung lengan\n• Lingkar dada 100 cm, panjang baju 53 cm\n\nOutfit simpel buat harian.\nCek di Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#OOTDIndo #OuterKekinian #JaketCrop #FashionWanita #RacunShopee",
                        "visual_note": "Foto sprint28_product_4.jpg: Bagan tabel ukuran LD 100 cm, PJ 53 cm, PJ lengan 60 cm"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Pernahkah Anda berdiri di depan lemari penuh pakaian tapi tetap merasa bingung mau pakai apa hari ini?\n\nBagi banyak perempuan aktif, kuncinya bukan memperbanyak isi lemari, melainkan memiliki sepotong pakaian luar (outer) dengan potongan terstruktur yang bisa dipadukan dengan berbagai atasan basic.",
                        "visual_note": "Foto kolase sprint28_product_1.jpg dan sprint28_product_3.jpg: Padu padan outer kasual elegan"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Kurasi spesifikasi Amora EMWEHA Jaket Crop:\n\n- Desain Pointed Front: Ujung depan meruncing memberikan efek siluet tubuh yang lebih ramping dan jenjang.\n- Kerah Kemeja Klasik: Menjaga impresi rapi untuk dipakai ke kantor santai maupun kumpul akhir pekan.\n- Slit Sleeve: Aksen belahan di pergelangan tangan yang leluasa dan mempermudah wudhu.\n- Ukuran Pas: Lingkar dada 100 cm, panjang badan 53 cm, dan panjang lengan 60 cm.\n\nPilihan praktis untuk upgrade gaya busana kasual harian.\nLink pembelian resmi di Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#FashionWanita #OuterHijab #JaketCrop #GayaKasual #BelanjaShopee",
                        "visual_note": "Foto sprint28_product_4.jpg: Rincian ukuran dan panduan sizing"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Satu outer buat banyak suasana: kuliah santai, meeting kasual, sampai nongkrong akhir pekan. ✨\n\nTanpa ribet mix and match lama di depan cermin, sentuhan cutting yang tepat bikin gaya harian langsung naik kelas.\n\nCek slide berikutnya untuk detail potongan dan panduan ukurannya. 👉",
                        "visual_note": "Carousel Slide 1: sprint28_product_1.jpg (Foto lookbook jaket crop Amora)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Detail spesifikasi Amora EMWEHA Jaket Crop:\n\n- Cutting pointed front modern & proporsional\n- Kerah kemeja rapi & timeless\n- Aksen slit lengan yang leluasa\n- Lingkar dada 100 cm, panjang baju 53 cm\n- Konsep fair price yang ramah anggaran\n\nPilihan tepat melengkapi koleksi luaran harian.\nLink checkout Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#JaketCropWanita #OOTDHarian #OuterCasual #FashionInspo #ShopeeHaul",
                        "visual_note": "Carousel Slide 2: sprint28_product_4.jpg (Size chart dan detail kerah)"
                    }
                }
            },
            {
                "angle_id": "angle-02",
                "angle_name": "Trik Siluet Jenjang Melalui Potongan Baju Runcing Depan",
                "target_trigger": "Fokus pada estetika visual, ilusi tubuh tinggi/ramping, dan detail arsitektur pakaian",
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Rahasia kelihatan lebih jenjang di foto OOTD sebetulnya bukan cuma sudut pengambilan kamera, tapi garis potongan baju.\n\nOuter dengan potongan bawah lurus rata sering membuat siluet tubuh terkesan kotak. Sebaliknya, potongan depan yang meruncing (pointed cut) secara visual memperpanjang garis pinggul ke bawah sehingga postur terlihat lebih proporsional.",
                        "visual_note": "Foto sprint28_product_1.jpg: Detail cutting runcing depan yang memberikan siluet ramping"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Detail rancangan Amora Jaket Crop EMWEHA ini fokus pada efek visual tersebut:\n• Potongan depan runcing (pointed front) memberi efek visual ramping\n• Kerah kemeja formal-kasual yang terstruktur rapi\n• Belahan di ujung lengan menambah sentuhan dinamis\n• Dimensi: LD 100 cm, panjang baju 53 cm, lengan 60 cm\n\nOuter stylish untuk pelengkap OOTD harian.\nLink belanja Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#JaketCropWanita #OOTDHijab #StylingTips #FashionCasual #ShopeeHaul",
                        "visual_note": "Foto sprint28_product_5.jpg: Tampilan keseluruhan siluet jaket dari depan"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Mengapa potongan baju tertentu bisa membuat seseorang tampak lebih proporsional saat difoto?\n\nJawabannya ada pada ilusi optik garis pakaian. Garis horizontal lurus cenderung membagi tubuh menjadi blok kaku, sedangkan garis diagonal atau meruncing ke bawah menciptakan kesan visual tubuh yang lebih panjang dan ramping.",
                        "visual_note": "Foto sprint28_product_1.jpg: Panduan visual efek cutting pointed front"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Bedah fitur jaket crop Amora EMWEHA:\n\n- Pointed Front Design: Garis depan meruncing secara visual mengarahkan pandangan ke bawah, menciptakan siluet lebih jenjang.\n- Kerah Kemeja Terstruktur: Menambah ketegasan di area bahu tanpa terasa kaku.\n- Detail Slit Cuff: Aksen modern pada pergelangan tangan yang fleksibel.\n- Spesifikasi Ukuran: LD 100 cm, panjang badan 53 cm, toleransi 1-2 cm.\n\nSolusi luaran harian yang anggun dan fungsional.\nLink pesanan Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#OuterKeren #TipsOutfit #FashionWanita #JaketCrop #ShopeeHaul",
                        "visual_note": "Foto sprint28_product_4.jpg: Detail spesifikasi teknis ukuran"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Visual trick yang bikin gaya harian kelihatan lebih jenjang dan rapi. ✨\n\nPotongan crop dengan aksen runcing di bagian depan memberikan garis siluet yang flattering dan modern.\n\nSimak kurasi spesifikasi produk di slide berikutnya. 👉",
                        "visual_note": "Carousel Slide 1: sprint28_product_1.jpg (Gaya kasual modern dengan jaket crop)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Rincian spesifikasi Amora Jaket Crop EMWEHA:\n\n- Desain crop pointed front yang mempertegas siluet\n- Kerah kemeja rapi untuk kesan smart look\n- Aksen slit lengan fungsional dan modis\n- LD 100 cm, panjang badan 53 cm, panjang lengan 60 cm\n\nTemukan kombinasi gaya terbaikmu.\nLink Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#OOTDStyle #CropJacket #RacunShopee #OuterWanita #CasualChic",
                        "visual_note": "Carousel Slide 2: sprint28_product_6.jpg (Detail jahitan dan finishing produk)"
                    }
                }
            },
            {
                "angle_id": "angle-03",
                "angle_name": "Konsep Fair Price: Tampil Percaya Diri Tanpa Menguras Anggaran",
                "target_trigger": "Koneksi emosional seputar self-love, apresiasi diri, dan belanja bijak berharga wajar",
                "threads": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Menghargai diri sendiri lewat outfit yang rapi dan nyaman gak selalu berarti harus beli baju mahal berlabel desainer.\n\nNilai sepotong pakaian sebetulnya ada pada bagaimana pakaian itu memberi rasa percaya diri dan kenyamanan saat dipakai beraktivitas sehari-hari. Pakaian yang tepat adalah yang potongannya pas dan harganya tetap masuk akal.",
                        "visual_note": "Foto sprint28_product_2.jpg: Filosofi Fair Price EMWEHA tentang pakaian nyaman dan wajar"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Filosofi 'Fair Price' pada Amora Jaket Crop EMWEHA membuktikan gaya modis tetap bisa terjangkau:\n• Cutting cropped depan runcing yang edgy & modern\n• Manset lengan berbelah (slit sleeve) yang leluasa\n• Kerah kemeja klasik serbaguna\n• Ukuran all-size: LD 100 cm, panjang baju 53 cm\n\nPilihan outfit harian yang bersahabat untuk perempuan aktif.\nCek di Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#RacunShopee #AmoraCrop #OuterWanita #OutfitKuliah #ShopeeFashion",
                        "visual_note": "Foto sprint28_product_1.jpg: Model memperlihatkan kenyamanan dan fleksibilitas jaket"
                    }
                },
                "facebook": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Setiap perempuan berhak tampil percaya diri dan mengekspresikan gaya terbaiknya tanpa harus merasa terbebani oleh harga pakaian yang tidak masuk akal.\n\nPakaian yang bernilai tinggi adalah pakaian yang menghadirkan rasa nyaman, membangun rasa percaya diri, dan siap menemani langkah produktif Anda setiap hari.",
                        "visual_note": "Foto sprint28_product_2.jpg: Manifesto filosofi Fair Price dari EMWEHA"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Keunggulan objektif Amora EMWEHA Jaket Crop:\n\n- Desain Cropped Pointed Front: Tampilan kekinian dengan siluet depan runcing yang modis.\n- Kerah Kemeja Rapi: Cocok untuk kegiatan santai hingga pertemuan kerja santai.\n- Lengan Slit Sleeve: Desain lengan berbelah untuk kenyamanan beraktivitas.\n- Ukuran Realistis: LD 100 cm, panjang 53 cm, lingkar ketiak 48 cm.\n\nSebuah langkah kecil untuk tampil lebih percaya diri setiap hari.\nLink pesanan resmi Shopee: https://s.shopee.co.id/20vxzX4Fx0\n\n#FairPrice #FashionBijak #OuterMuslimah #OOTDIndonesia #BelanjaShopee",
                        "visual_note": "Foto sprint28_product_3.jpg: Detail bahan dan siluet pakaian"
                    }
                },
                "instagram": {
                    "post_1": {
                        "type": "hook_relatable",
                        "caption": "Tampil percaya diri setiap hari berawal dari outfit yang nyaman dan pas di badan. ✨\n\nTanpa harus berlebihan, desain yang simpel dan berkarakter siap menemani rutinitas harianmu dengan penuh percaya diri.\n\nGeser untuk melihat detail cutting dan spesifikasi lengkapnya. 👉",
                        "visual_note": "Carousel Slide 1: sprint28_product_2.jpg (Brand message Fair Price EMWEHA)"
                    },
                    "post_2": {
                        "type": "spec_curation_cta",
                        "caption": "Fitur unggulan Amora Jaket Crop EMWEHA:\n\n- Desain cropped dengan potongan depan runcing\n- Kerah kemeja rapi & timeless look\n- Detail belahan ujung lengan praktis\n- Dimensi LD 100 cm, panjang baju 53 cm\n- Harga wajar dengan kualitas kurasi terpercaya\n\nTemukan outfit favorit barumu di Shopee.\nLink produk: https://s.shopee.co.id/20vxzX4Fx0\n\n#OutfitWanita #JaketCrop #ModestFashion #FashionBerkelas #ShopeeID",
                        "visual_note": "Carousel Slide 2: sprint28_product_1.jpg (Lookbook jaket crop Amora)"
                    }
                }
            }
        ],
        "material_spec_summary": {
            "product_highlight": "Amora EMWEHA Jaket Crop Wanita",
            "key_properties": [
                "Desain Crop Pointed Front: Potongan depan runcing yang memberi efek visual jenjang dan siluet ramping",
                "Kerah Kemeja Klasik: Memberikan sentuhan rapi, timeless, dan mudah dipadukan untuk gaya kasual maupun semi-formal",
                "Detail Slit Sleeves (Belahan Ujung Lengan): Aksen modern edgy sekaligus memudahkan gerak tangan dan wudhu-friendly",
                "Dimensi Proporsional: Lingkar Dada 100 cm, Panjang Baju 53 cm, Panjang Lengan 60 cm, Lingkar Ketiak 48 cm, Lebar Bahu 12 cm",
                "Konsep Fair Price EMWEHA: Value-for-money tinggi untuk perempuan tampil percaya diri dengan pakaian berkualitas tanpa overprice"
            ]
        },
        "platform_strategy": {
            "threads": {
                "primary_focus": "Diskusi teks tajam, punchline kalimat pertama, observasi outfit harian wanita, kurasi spesifikasi objektif",
                "format": "Thread 2-post bersambung (Post 1: Situasional hook/pain point, Post 2: Spek teknis + CTA link Shopee)",
                "recommended_posting_hours_wib": [
                    "07:30-09:00",
                    "12:00-13:30",
                    "19:00-21:30"
                ]
            },
            "facebook": {
                "primary_focus": "Storytelling observatif wanita aktif, listicle ringkas fungsi teknis, nada bersahabat dan suportif",
                "format": "Post 1 naratif relatable + Post 2 kurasi spek lengkap + link Shopee di badan postingan",
                "recommended_posting_hours_wib": [
                    "08:00-10:00",
                    "13:00-15:00",
                    "19:30-21:00"
                ]
            },
            "instagram": {
                "primary_focus": "Visual showcase cutting crop pointed front & detail slit cuffs, micro-blogging carousel, punchy caption",
                "format": "Carousel multi-slide + caption kurasi ringkas, CTA mengarahkan ke link bio/Shopee",
                "recommended_posting_hours_wib": [
                    "11:30-13:00",
                    "17:30-19:00",
                    "20:00-22:00"
                ]
            }
        }
    }

    # Validation of Threads character limits, forbidden claims, affiliate links, and hashtag counts
    print("--- VALIDATION REPORT ---")
    all_valid = True
    forbidden_claims = ["aku sudah", "aku pake", "saya sudah", "saya pake", "beneran tahan di bibir", "sudah kupakai"]

    for idx, angle in enumerate(data["campaign"]["copywriting_angles"]):
        print(f"\nChecking Angle {idx+1}: {angle['angle_name']}")
        for platform in ["threads", "facebook", "instagram"]:
            for post_key in ["post_1", "post_2"]:
                post_data = angle[platform][post_key]
                cap = post_data["caption"]
                length = len(cap)
                print(f"  [{platform.upper()}] {post_key} length: {length} chars")

                # Threads strict max limit
                if platform == "threads" and length > 500:
                    print(f"  ERROR: {platform} {post_key} exceeds 500 chars limit! ({length})")
                    all_valid = False

                # Forbidden personal claims
                for claim in forbidden_claims:
                    if claim in cap.lower():
                        print(f"  ERROR: Found forbidden claim '{claim}' in {platform} {post_key}")
                        all_valid = False

                # Affiliate link presence in post_2
                if post_key == "post_2":
                    if affiliate_url not in cap:
                        print(f"  ERROR: Affiliate link missing in {platform} {post_key}!")
                        all_valid = False

                # Hashtags check in post_2
                if post_key == "post_2":
                    tags = re.findall(r"#\w+", cap)
                    print(f"  [{platform.upper()}] {post_key} hashtags ({len(tags)}): {' '.join(tags)}")
                    if not (3 <= len(tags) <= 5):
                        print(f"  ERROR: Hashtag count {len(tags)} not between 3 and 5 in {platform} {post_key}!")
                        all_valid = False

    if not all_valid:
        raise ValueError("Validation failed! Please fix issues before saving.")

    with open("docs/sprint28_campaign.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("\nSuccessfully updated docs/sprint28_campaign.json!")

if __name__ == "__main__":
    generate_sprint28_data()
