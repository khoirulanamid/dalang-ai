#!/usr/bin/env python3
"""
Enrich sprint30_campaign.json with Gathot viral copywriting strategy,
threads thread-split posts, multi-channel platform strategy, and media metadata.
Complies with standards/gathot_social_standards.md.
"""
import os
import json
from datetime import datetime, timezone

CAMPAIGN_FILE = "docs/sprint30_campaign.json"
IMG_DIR = "workspace/product_images/sprint30"
AFFILIATE_URL = "https://s.shopee.co.id/80DBs5lgX2"

def main():
    if not os.path.exists(CAMPAIGN_FILE):
        raise FileNotFoundError(f"Campaign file {CAMPAIGN_FILE} does not exist.")

    with open(CAMPAIGN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Media Assets Cataloging
    assets = []
    if os.path.exists(IMG_DIR):
        files = sorted(os.listdir(IMG_DIR))
        for fname in files:
            fpath = os.path.join(IMG_DIR, fname)
            if os.path.isfile(fpath) and fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                size = os.path.getsize(fpath)
                mime = "image/png" if fname.lower().endswith('.png') else "image/jpeg"
                assets.append({
                    "file_name": fname,
                    "primary_path": fpath,
                    "file_size_bytes": size,
                    "mime_type": mime
                })

    data["media"] = {
        "target_directory": IMG_DIR,
        "total_downloaded": len(assets),
        "assets": assets
    }

    # 2. Product Identifiers and Categorization
    data["product_id"] = "inbex-tf-3366-tripod-remote-133cm"
    data["source_url"] = AFFILIATE_URL
    data["affiliate_url"] = AFFILIATE_URL
    data["status"] = "ready_for_campaign"
    data["category"] = "Fotografi / Tripod, Monopod & Aksesoris"

    # Enriched Price if missing
    if not data.get("price") or not isinstance(data.get("price"), dict):
        data["price"] = {
            "currency": "IDR",
            "amount": 55000.0,
            "formatted": "Rp55.000"
        }

    # Structured Specifications
    data["specs"] = [
        "Tinggi operasional maksimal 133 cm, tinggi minimal 50 cm, panjang saat dilipat 50 cm",
        "Dilengkapi remote shutter Bluetooth bersertifikat resmi POSTEL (No: 87156/SDPPI/2022)",
        "Kepala tripod 3-way pan head dengan dudukan sekrup universal 1/4 inci",
        "Rangka 3-section flip-lock leg mechanism dengan bantalan karet anti-slip",
        "Kapasitas beban maksimum hingga 3.0 kg, kompatibel untuk smartphone, DSLR, mirrorless, dan action camera",
        "Paket penjualan lengkap: 1x Tripod TF-3366, 1x Bluetooth Remote, 1x Phone Holder U, 1x Carry Bag"
    ]

    # 3. Campaign Strategy
    target_audience = (
        "Konten kreator pemula, video podcaster mandiri, vlogger ponsel, mahasiswa/pelajar untuk "
        "presentasi video, penjual online/UMKM untuk live streaming produk, serta penggemar fotografi mobile "
        "usia 18-38 tahun yang membutuhkan penyangga kamera tinggi, stabil, dan mudah dibawa bepergian."
    )

    key_selling_points = [
        "Ketinggian fleksibel hingga 133 cm yang sejajar pandangan mata tanpa perlu meja tambahan",
        "Remote shutter Bluetooth bersertifikat POSTEL memungkinkan jepret foto dan rekam video nirkabel mandiri",
        "Sistem kepala 3-way pan head memudahkan rotasi 360 derajat serta orientasi video lanskap maupun potret",
        "Bobot ringan sekitar 700 gram lengkap dengan tas jinjing (carry bag) untuk mobilitas tinggi",
        "Paket bundling lengkap langsung pakai dengan holder smartphone model U dan ulir 1/4 inci untuk kamera SLR"
    ]

    threads_viral_strategy = {
        "compliance": "Sesuai standar Gathot: Tanpa klaim konsumsi pribadi palsu ('aku/saya sudah pakai'), tanpa emoji berlebihan, karakter Threads <= 500 per post, link affiliate resmi Shopee, hashtag terarah 3-5 tags.",
        "core_narrative": "Mengangkat dilema harian kreator solo atau vlogger yang kerepotan merekam diri sendiri tanpa bantuan teman, sudut video miring karena sandaran darurat, serta solusi praktis tripod portabel lengkap dengan remote shutter Bluetooth resmi dan tas bawaan.",
        "framework": "Post 1: Hook relatable problem / situasi komedi kreatif tanpa klaim palsu. Post 2: Kurasi spesifikasi teknis objektif, keunggulan fungsional, call-to-action link resmi Shopee, dan hashtag relevan."
    }

    data["campaign_strategy"] = {
        "target_audience": target_audience,
        "key_selling_points": key_selling_points,
        "threads_viral_strategy": threads_viral_strategy
    }

    # 4. Copywriting Angles (Thread Split + Facebook + Instagram)
    copywriting_angles = [
        {
            "angle_id": "angle-01",
            "angle_name": "Dilema Kreator Solo Merekam Video Tanpa Bantuan Orang Lain",
            "target_trigger": "Frustrasi kreator mandiri saat harus menyandarkan HP di botol minum atau tumpukan buku yang gampang roboh",
            "threads": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Tantangan terbesar bikin video sendiri di rumah: HP disandarkan di botol minum, baru hitungan mundur detik kedua botolnya sudah menggelinding.\n\nMomen rekaman yang mestinya natural malah berakhir jadi komedi di balik layar karena sudut kamera miring atau HP jatuh ke lantai.\n\nBanyak pembuat konten solo mencari tripod yang tingginya cukup sejajar pandangan mata tanpa perlu meja tambahan.",
                    "visual_note": "Foto product_image_01.jpg: Overview tripod INBEX TF-3366 terpasang dengan smartphone dan remote bluetooth"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Tripod INBEX TF-3366 hadir sebagai solusi setup ringkas:\n\n- Rentang tinggi 50 cm hingga 133 cm dengan sistem flip lock\n- Termasuk remote Bluetooth bersertifikat POSTEL\n- 3-way pan head untuk orientasi vertikal maupun horizontal\n- Dudukan holder U dan carry bag sudah tersedia dalam paket\n\nCek detail spesifikasi lengkapnya di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#TripodHP #VlogSetup #InbexTripod #AksesorisKamera #ShopeeHaul",
                    "visual_note": "Foto product_image_16.jpg: Detail mekanisme pengunci kaki flip lock dan kepala tripod INBEX"
                }
            },
            "facebook": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Bagi konten kreator yang sering memproduksi video secara mandiri, salah satu kendala paling merepotkan adalah mencari sudut rekaman yang stabil. Meletakkan ponsel di atas tumpukan buku, cangkir, atau senderan botol sering kali berujung jatuh di tengah rekaman.\n\nMenggunakan tripod dengan ketinggian fleksibel dan kepala pan-head yang bisa diatur membuat proses rekaman solo menjadi jauh lebih terstruktur dan efisien.",
                    "visual_note": "Foto product_image_01.jpg: Overview tripod INBEX TF-3366 di setup studio"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Spesifikasi utama INBEX TF-3366 Tripod 133cm:\n\n1. Rentang Ketinggian: 50 cm hingga 133 cm dengan pengunci kaki flip-lock yang kokoh.\n2. Remote Shutter Bluetooth: Koneksi nirkabel bersertifikat resmi POSTEL (87156/SDPPI/2022) untuk memicu tombol rekam/foto dari jarak jauh.\n3. Kepala 3-Way Pan Head: Fleksibel untuk perekaman sudut lanskap maupun potret.\n4. Perlengkapan Lengkap: Disertai holder HP tipe U dan tas jinjing (carry bag).\n\nCek spesifikasi dan ketersediaan unit di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#VlogKamera #TripodHP #InbexTripod #SetupKreator #ShopeeID",
                    "visual_note": "Foto product_image_16.jpg: Detail bagian kepala 3-way pan head dan kaki tripod"
                }
            },
            "instagram": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Setup rekaman solo sering berantakan cuma gara-gara HP jatuh dari sandaran darurat? Saatnya beralih ke tripod proporsional.\n\nINBEX TF-3366 hadir dengan tinggi maksimal 133 cm dan remote Bluetooth resmi POSTEL. Cocok untuk vlogging, reels, maupun foto mandiri tanpa repot cari bantuan.\n\nCek link di bio untuk katalog Shopee resmi:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#TripodHP #KreatorIndonesia #VlogSetup #Inbex #ShopeeHaul",
                    "visual_note": "Carousel Slide 1: product_image_01.jpg (Foto tripod INBEX berdiri kokoh dengan ponsel)"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Kurasi ringkas keunggulan tripod portabel INBEX TF-3366:\n- Ketinggian dapat diatur 50 - 133 cm\n- Kepala 3-way pan head untuk orientasi vertikal & horizontal\n- Shutter Bluetooth tersertifikasi POSTEL\n- Kaki anti-slip karet kokoh dan stabil\n- Termasuk U-holder ponsel & carry bag\n\nKunjungi etalase resmi di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#FotografiPonsel #AksesorisHP #InbexTripod #KontenKreator #ShopeeFinds",
                    "visual_note": "Carousel Slide 2: product_image_04.jpg (Foto kelengkapan paket tripod dan tas bawaan)"
                }
            }
        },
        {
            "angle_id": "angle-02",
            "angle_name": "Solusi Foto Bareng & Konten OOTD Tanpa Merepotkan Orang Lain",
            "target_trigger": "Keinginan foto grup atau dokumentasi OOTD rapi saat bepergian tanpa canggung meminta tolong orang asing",
            "threads": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Pernah minta tolong orang asing fotoin pas jalan-jalan, terus pas dicek hasilnya: kaki kepotong, kepala kepotong, fokusnya malah ke tiang listrik di belakang?\n\nMomen liburan atau foto bareng sering terlewat cuma karena tidak ada yang stand by pegang kamera.\n\nSolusi paling aman untuk foto full body atau group photo adalah tripod yang stabil dengan remote nirkabel mandiri.",
                    "visual_note": "Foto product_image_02.jpg: Tripod INBEX TF-3366 diperluas hingga 133cm menunjukkan kestabilan posisi"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Kurasi teknis INBEX TF-3366 untuk dokumentasi harian:\n\n- Ketinggian maksimal 133 cm, pas untuk framing sejajar dada dan mata\n- Shutter nirkabel Bluetooth (POSTEL 87156/SDPPI/2022) tanpa kabel menjuntai\n- Rangka aluminium alloy dengan beban tampung sampai 3 kg\n- Kaki karet anti-slip stabil di lantai maupun aspal\n\nLihat ketersediaan dan penawaran resmi di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#FotografiPonsel #TripodKamera #Inbex #OOTDIndo #ShopeeFinds",
                    "visual_note": "Foto product_image_05.jpg: Detail holder HP U dan konektor sekrup universal 1/4 inci"
                }
            },
            "facebook": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Foto OOTD atau momen kebersamaan sering kali terkendala ketiadaan orang yang bisa dimintai tolong mengambil foto dengan framing proporsional. Hasil foto dari orang lewat pun terkadang kurang pas dengan komposisi yang diinginkan.\n\nMembawa tripod portabel dengan remote shutter Bluetooth memberikan keleluasaan penuh untuk mengatur angle dan ekspresi tanpa terburu-buru.",
                    "visual_note": "Foto product_image_02.jpg: Penggunaan tripod INBEX untuk foto full body"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Keunggulan INBEX TF-3366 untuk fotografi mobile:\n\n- Bobot ringan sekitar 700 gram, mudah dibawa dalam tas selempang bawaan\n- Remote Bluetooth kompatibel dengan Android dan iOS tanpa instalasi aplikasi tambahan\n- Beban maksimal 3 kg, aman untuk smartphone maupun kamera mirrorless\n- Mekanisme pengunci kaki 3 tingkat yang praktis dan cepat disetel\n\nInformasi produk dan pemesanan di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#FotoOOTD #TripodBluetooth #InbexIndonesia #GadgetTravel #ShopeeHaul",
                    "visual_note": "Foto product_image_05.jpg: U-holder dan mekanisme pengunci ponsel"
                }
            },
            "instagram": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Niat hati mau foto OOTD estetik, tapi hasil jepretan teman malah buram atau miring? Pakai tripod mandiri solusinya.\n\nINBEX TF-3366 hadir dengan tinggi 133 cm dan remote Bluetooth shutter resmi. Pasang, atur framing, langsung jepret sendiri dari kejauhan.\n\nCek produknya di link Shopee bio:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#OOTDStyle #TripodHP #InbexPhotography #AksesorisFoto #ShopeeID",
                    "visual_note": "Carousel Slide 1: product_image_02.jpg (Demonstrasi ketinggian tripod 133cm)"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Fitur unggulan INBEX TF-3366:\n- Maksimal tinggi 133 cm (lipat 50 cm)\n- Bobot ringan ~700g + tas travel praktis\n- Remote Bluetooth sertifikasi POSTEL\n- Kompatibel HP, mirrorless, dan action cam\n- Kaki karet anti-slip kokoh\n\nCek penawaran langsung di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#TripodBluetooth #GadgetMurah #Inbex #ReviewAksesoris #ShopeeLook",
                    "visual_note": "Carousel Slide 2: product_image_05.jpg (Tampilan detail holder ponsel dan ulir tripod)"
                }
            }
        },
        {
            "angle_id": "angle-03",
            "angle_name": "Stabilitas Rekaman Live Streaming dan Belajar Daring di Meja",
            "target_trigger": "Ponsel sering goyang atau panas saat live shopping dan video call kerja/sekolah berjam-jam",
            "threads": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Mengikuti sesi live streaming atau video meeting 2 jam sambil pegang HP manual itu melelahkan, belum lagi layarnya goyang terus setiap tangan ganti posisi.\n\nBahkan sandaran HP mini di meja sering tidak cukup tinggi, membuat postur tubuh membungkuk dan sudut kamera jadi kurang proporsional.\n\nPenyangga dengan pengaturan tinggi fleksibel dari level meja hingga berdiri jadi kebutuhan dasar.",
                    "visual_note": "Foto product_image_03.jpg: Detail remote bluetooth dan mount holder tripod INBEX TF-3366"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Spesifikasi INBEX TF-3366 untuk pendukung siaran langsung:\n\n- Pengaturan ketinggian multi-level mulai 50 cm hingga 133 cm\n- Quick release plate standar 1/4 inci untuk kamera mirrorless maupun holder ponsel\n- Tuas putar 360 derajat untuk panning halus saat demonstrasi produk\n- Bobot ringan hanya sekitar 700 gram, mudah dipindahkan\n\nCek rincian produk di toko resmi Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#LiveStreaming #TripodPonsel #InbexIndonesia #WorkFromHome #ShopeeID",
                    "visual_note": "Foto product_image_06.jpg: Konstruksi tripod kokoh untuk penggunaan di meja maupun lantai"
                }
            },
            "facebook": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Siaran langsung untuk jualan online atau sesi video conference yang berlangsung lama membutuhkan penyangga kamera yang kokoh. Sandaran meja kecil kerap kali tidak memberikan sudut pandang yang proporsional sehingga pembicara harus terus menunduk.\n\nDengan tripod fleksibel yang bisa disesuaikan tingginya dari 50 cm hingga 133 cm, posisi kamera bisa diatur tepat setinggi mata tanpa membebani leher dan tangan.",
                    "visual_note": "Foto product_image_03.jpg: Tripod INBEX digunakan untuk keperluan siaran langsung"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Rangkuman spesifikasi teknis INBEX TF-3366:\n\n1. Kestabilan: Rangka 3 tingkat dengan flip lock dan alas karet anti-selip.\n2. Ergonomi: Tuas 3-way pan head memudahkan pengaturan sudut vertikal maupun horizontal.\n3. Aksesoris Tambahan: Remote Bluetooth nirkabel dan holder ponsel U sudah disertakan dalam paket.\n4. Standar Industri: Dilengkapi ulir baut 1/4 inci untuk kamera mirrorless dan digital.\n\nLink toko resmi di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#LiveStreamingBisnis #TripodPonsel #InbexTripod #AksesorisOnlineShop #ShopeeID",
                    "visual_note": "Foto product_image_06.jpg: Tampilan 3-way head dan ulir sekrup universal"
                }
            },
            "instagram": {
                "post_1": {
                    "type": "hook_relatable",
                    "caption": "Sering pegal pegang HP saat live streaming atau webinar berjam-jam? Angle kamera menunduk bikin tampilan kurang profesional.\n\nINBEX TF-3366 punya rentang tinggi 50 sampai 133 cm. Posisi kamera pas di level mata, stabil tanpa goyang.\n\nCek produknya di tautan Shopee bio:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#LiveStreamSetup #TripodHP #InbexIndonesia #WorkFromHome #ShopeeHaul",
                    "visual_note": "Carousel Slide 1: product_image_03.jpg (Tripod INBEX pada konfigurasi live stream meja)"
                },
                "post_2": {
                    "type": "spec_curation_cta",
                    "caption": "Kelebihan INBEX TF-3366 untuk konten kreator & live seller:\n- Ketinggian multi-level 50 - 133 cm\n- Kepala 3-way pan head fleksibel 360 derajat\n- Holder smartphone tipe U kokoh\n- Dilengkapi remote shutter Bluetooth resmi POSTEL\n- Kaki karet stabil di berbagai permukaan\n\nKunjungi etalase resmi di Shopee:\nhttps://s.shopee.co.id/80DBs5lgX2\n\n#SetupLive #AksesorisHP #TripodKamera #Inbex #ShopeeID",
                    "visual_note": "Carousel Slide 2: product_image_06.jpg (Detail stabilitas kaki dan engsel pan head)"
                }
            }
        }
    ]

    # 5. Omnichannel Campaign Object
    data["campaign"] = {
        "campaign_id": "sprint30",
        "campaign_name": "INBEX TF-3366 Tripod Remote Omnichannel Campaign",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_audience": target_audience,
        "copywriting_angles": copywriting_angles,
        "material_spec_summary": {
            "model": "INBEX TF-3366",
            "material": "Aluminium alloy & ABS",
            "max_height_cm": 133,
            "min_height_cm": 50,
            "folded_length_cm": 50,
            "max_payload_kg": 3.0,
            "postel_cert": "87156/SDPPI/2022",
            "included_accessories": ["Bluetooth Remote Shutter", "U-Type Phone Holder", "Carry Bag"]
        },
        "platform_strategy": {
            "threads": {
                "primary_focus": "Diskusi santai seputar dilema teknis konten mandiri, thread-splitting hook & spec-curation, punchline di kalimat awal, 3-5 hashtag relevan.",
                "format": "Thread 2-post bersambung: Post 1 relatable hook & dilemma, Post 2 kurasi spek objektif + CTA Shopee link.",
                "recommended_posting_hours_wib": [
                    "07:30-09:00",
                    "12:00-13:30",
                    "19:00-21:30"
                ]
            },
            "facebook": {
                "primary_focus": "Artikel naratif informatif, edukasi setup fotografi/vlog praktis untuk audiens keluarga, UMKM live streaming, dan traveler.",
                "format": "Post naratif 2 bagian (Pain point & Solusi spesifikasi teknis), gambar produk resolusi tinggi, CTA Shopee link.",
                "recommended_posting_hours_wib": [
                    "08:00-10:00",
                    "13:00-15:00",
                    "19:30-21:00"
                ]
            },
            "instagram": {
                "primary_focus": "Visual showcase tripod INBEX TF-3366, micro-blogging carousel, punchy caption dengan CTA terarah ke link bio/Shopee.",
                "format": "Carousel multi-slide + caption kurasi ringkas, CTA mengarahkan ke link bio/Shopee.",
                "recommended_posting_hours_wib": [
                    "11:30-13:00",
                    "17:30-19:00",
                    "20:00-22:00"
                ]
            }
        }
    }

    with open(CAMPAIGN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully enriched {CAMPAIGN_FILE}")
    print(f"- Total media assets cataloged: {len(assets)}")
    print(f"- Copywriting angles created: {len(copywriting_angles)}")
    print(f"- Affiliate URL: {AFFILIATE_URL}")

if __name__ == "__main__":
    main()
