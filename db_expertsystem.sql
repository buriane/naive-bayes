/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS db_expertsystem;
USE db_expertsystem;

DROP TABLE IF EXISTS `aturangejala`;
CREATE TABLE `aturangejala` (
  `id_aturanGejala` bigint NOT NULL,
  `id_detailAturan` bigint DEFAULT NULL,
  PRIMARY KEY (`id_aturanGejala`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `detailaturan`;
CREATE TABLE `detailaturan` (
  `id_detailAturan` bigint NOT NULL,
  `id_gejala` bigint DEFAULT NULL,
  PRIMARY KEY (`id_detailAturan`),
  KEY `id_gejala` (`id_gejala`),
  CONSTRAINT `detailaturan_ibfk_1` FOREIGN KEY (`id_gejala`) REFERENCES `gejala` (`id_gejala`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `diagnosis`;
CREATE TABLE `diagnosis` (
  `id_diagnosis` bigint NOT NULL,
  `nama_diagnosis` varchar(255) DEFAULT NULL,
  `deskripsi_diagnosis` text,
  `gambar_diagnosis` text,
  `solusi_diagnosis` text,
  PRIMARY KEY (`id_diagnosis`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `gejala`;
CREATE TABLE `gejala` (
  `id_gejala` bigint NOT NULL,
  `nama_gejala` varchar(255) DEFAULT NULL,
  `kode_gejala` varchar(100) DEFAULT NULL,
  `pertanyaan_gejala` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_gejala`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `laporandiagnosis`;
CREATE TABLE `laporandiagnosis` (
  `id_laporanDiagnosis` bigint NOT NULL,
  `id_pengguna` bigint DEFAULT NULL,
  `id_diagnosis` bigint DEFAULT NULL,
  `tanggal_diagnosis` date DEFAULT NULL,
  `probabilitas` float DEFAULT NULL,
  PRIMARY KEY (`id_laporanDiagnosis`),
  KEY `id_pengguna` (`id_pengguna`),
  KEY `id_diagnosis` (`id_diagnosis`),
  CONSTRAINT `laporandiagnosis_ibfk_1` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`),
  CONSTRAINT `laporandiagnosis_ibfk_2` FOREIGN KEY (`id_diagnosis`) REFERENCES `diagnosis` (`id_diagnosis`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `laporangejala`;
CREATE TABLE `laporangejala` (
  `id_laporanGejala` bigint NOT NULL,
  `id_laporanDiagnosis` bigint DEFAULT NULL,
  `id_gejala` bigint DEFAULT NULL,
  `value` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_laporanGejala`),
  KEY `id_laporanDiagnosis` (`id_laporanDiagnosis`),
  KEY `id_gejala` (`id_gejala`),
  CONSTRAINT `laporangejala_ibfk_1` FOREIGN KEY (`id_laporanDiagnosis`) REFERENCES `laporandiagnosis` (`id_laporanDiagnosis`),
  CONSTRAINT `laporangejala_ibfk_2` FOREIGN KEY (`id_gejala`) REFERENCES `gejala` (`id_gejala`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `pengguna`;
CREATE TABLE `pengguna` (
  `id_pengguna` bigint NOT NULL,
  `nama_pengguna` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` enum('admin','user') DEFAULT NULL,
  PRIMARY KEY (`id_pengguna`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `aturangejala` (`id_aturanGejala`, `id_detailAturan`) VALUES
(1, 1);
INSERT INTO `aturangejala` (`id_aturanGejala`, `id_detailAturan`) VALUES
(2, 2);
INSERT INTO `aturangejala` (`id_aturanGejala`, `id_detailAturan`) VALUES
(3, 3);
INSERT INTO `aturangejala` (`id_aturanGejala`, `id_detailAturan`) VALUES
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10),
(11, 11),
(12, 12),
(13, 13),
(14, 14),
(15, 15),
(16, 16),
(17, 17),
(18, 18),
(19, 19),
(20, 20),
(21, 21),
(22, 22),
(23, 23),
(24, 24),
(25, 25),
(26, 26),
(27, 27),
(28, 28),
(29, 29),
(30, 30);

INSERT INTO `detailaturan` (`id_detailAturan`, `id_gejala`) VALUES
(1, 1);
INSERT INTO `detailaturan` (`id_detailAturan`, `id_gejala`) VALUES
(2, 2);
INSERT INTO `detailaturan` (`id_detailAturan`, `id_gejala`) VALUES
(3, 3);
INSERT INTO `detailaturan` (`id_detailAturan`, `id_gejala`) VALUES
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10),
(11, 11),
(12, 12),
(13, 13),
(14, 14),
(15, 15),
(16, 16),
(17, 17),
(18, 18),
(19, 19),
(20, 20),
(21, 21),
(22, 22),
(23, 23),
(24, 24),
(25, 25),
(26, 26),
(27, 27),
(28, 28),
(29, 29),
(30, 30);

INSERT INTO `diagnosis` (`id_diagnosis`, `nama_diagnosis`, `deskripsi_diagnosis`, `gambar_diagnosis`, `solusi_diagnosis`) VALUES
(1, 'Penyakit Jantung Koroner', 'Penyumbatan pembuluh darah jantung.', '/img/diagnosis1.png', 'Lakukan diet rendah lemak dan olahraga.');
INSERT INTO `diagnosis` (`id_diagnosis`, `nama_diagnosis`, `deskripsi_diagnosis`, `gambar_diagnosis`, `solusi_diagnosis`) VALUES
(2, 'Gagal Jantung', 'Ketidakmampuan jantung memompa darah dengan efisien.', '/img/diagnosis2.png', 'Konsumsi obat rutin dan hindari stres.');
INSERT INTO `diagnosis` (`id_diagnosis`, `nama_diagnosis`, `deskripsi_diagnosis`, `gambar_diagnosis`, `solusi_diagnosis`) VALUES
(3, 'Aritmia', 'Gangguan irama jantung.', '/img/diagnosis3.png', 'Konsultasikan dengan dokter spesialis jantung.');
INSERT INTO `diagnosis` (`id_diagnosis`, `nama_diagnosis`, `deskripsi_diagnosis`, `gambar_diagnosis`, `solusi_diagnosis`) VALUES
(4, 'Kardiomiopati', 'Pelemahan otot jantung.', '/img/diagnosis4.png', 'Batasi aktivitas berat dan rutin periksa.'),
(5, 'Infark Miokard Akut', 'Serangan jantung akibat penyumbatan mendadak.', '/img/diagnosis5.png', 'Segera tangani medis, lanjutkan pengobatan.'),
(6, 'Hipertensi', 'Tekanan darah tinggi kronis.', '/img/diagnosis6.png', 'Kurangi konsumsi garam dan rutin cek tekanan darah.'),
(7, 'Angina Stabil', 'Nyeri dada yang berulang karena aktivitas.', '/img/diagnosis7.png', 'Hindari aktivitas berat, konsumsi nitrat.'),
(8, 'Perikarditis', 'Peradangan pada selaput jantung.', '/img/diagnosis8.png', 'Konsumsi antiinflamasi dan istirahat cukup.'),
(9, 'Endokarditis', 'Infeksi pada katup jantung.', '/img/diagnosis9.png', 'Antibiotik jangka panjang, kontrol infeksi.'),
(10, 'Miokarditis', 'Infeksi otot jantung.', '/img/diagnosis10.png', 'Antivirus/antibiotik dan istirahat total.'),
(11, 'Aterosklerosis', 'Pengerasan pembuluh darah.', '/img/diagnosis11.png', 'Olahraga rutin dan diet sehat.'),
(12, 'Fibrilasi Atrium', 'Denyut jantung tidak teratur.', '/img/diagnosis12.png', 'Obat pengatur ritme jantung.'),
(13, 'Bradiaritmia', 'Denyut jantung terlalu lambat.', '/img/diagnosis13.png', 'Pemasangan pacu jantung.'),
(14, 'Tachycardia', 'Denyut jantung terlalu cepat.', '/img/diagnosis14.png', 'Pemberian beta blocker.'),
(15, 'Hipotensi', 'Tekanan darah rendah.', '/img/diagnosis15.png', 'Konsumsi cairan dan garam.'),
(16, 'Stenosis Katup Mitral', 'Penyempitan katup jantung.', '/img/diagnosis16.png', 'Pembedahan atau penggantian katup.'),
(17, 'Stenosis Aorta', 'Penyempitan katup aorta.', '/img/diagnosis17.png', 'Operasi penggantian katup.'),
(18, 'PFO (Patent Foramen Ovale)', 'Lubang di atrium jantung.', '/img/diagnosis18.png', 'Tindakan kateter atau operasi.'),
(19, 'Iskemia Miokard', 'Kurangnya suplai darah ke otot jantung.', '/img/diagnosis19.png', 'Obat pengencer darah dan angioplasti.'),
(20, 'Serangan Jantung Ringan', 'Infark miokard minor.', '/img/diagnosis20.png', 'Perubahan gaya hidup dan terapi.'),
(21, 'Cardiac Arrest', 'Jantung berhenti mendadak.', '/img/diagnosis21.png', 'CPR dan AED darurat.'),
(22, 'Diseksi Aorta', 'Robeknya lapisan dalam aorta.', '/img/diagnosis22.png', 'Operasi segera.'),
(23, 'Penyakit Jantung Bawaan', 'Cacat jantung sejak lahir.', '/img/diagnosis23.png', 'Tindakan operasi korektif.'),
(24, 'Jantung Rematik', 'Kerusakan katup karena demam rematik.', '/img/diagnosis24.png', 'Antibiotik dan operasi jika perlu.'),
(25, 'Hipertrofi Ventrikel', 'Penebalan otot ventrikel.', '/img/diagnosis25.png', 'Pantau tekanan darah dan terapi.'),
(26, 'Tamponade Jantung', 'Penekanan jantung oleh cairan.', '/img/diagnosis26.png', 'Evakuasi cairan segera.'),
(27, 'Penyakit Katup Trikuspid', 'Gangguan pada katup trikuspid.', '/img/diagnosis27.png', 'Reparasi atau penggantian katup.'),
(28, 'Ventrikel Prematur', 'Kontraksi jantung tidak normal.', '/img/diagnosis28.png', 'Observasi atau terapi jika parah.'),
(29, 'Penyakit Arteri Perifer', 'Sumbatan pembuluh darah luar jantung.', '/img/diagnosis29.png', 'Terapi aliran darah dan operasi.'),
(30, 'Sindrom Brugada', 'Gangguan genetik ritme jantung.', '/img/diagnosis30.png', 'Pemasangan defibrilator implan.');

INSERT INTO `gejala` (`id_gejala`, `nama_gejala`, `kode_gejala`, `pertanyaan_gejala`) VALUES
(1, 'Nyeri Dada', 'G001', 'Apakah Anda merasakan nyeri dada?');
INSERT INTO `gejala` (`id_gejala`, `nama_gejala`, `kode_gejala`, `pertanyaan_gejala`) VALUES
(2, 'Sesak Napas', 'G002', 'Apakah Anda merasa sesak napas?');
INSERT INTO `gejala` (`id_gejala`, `nama_gejala`, `kode_gejala`, `pertanyaan_gejala`) VALUES
(3, 'Mudah Lelah', 'G003', 'Apakah Anda merasa mudah lelah?');
INSERT INTO `gejala` (`id_gejala`, `nama_gejala`, `kode_gejala`, `pertanyaan_gejala`) VALUES
(4, 'Detak Jantung Tidak Teratur', 'G004', 'Apakah detak jantung Anda tidak teratur?'),
(5, 'Pusing', 'G005', 'Apakah Anda sering merasa pusing?'),
(6, 'Mual', 'G006', 'Apakah Anda sering merasa mual?'),
(7, 'Keringat Dingin', 'G007', 'Apakah Anda berkeringat dingin?'),
(8, 'Nyeri di Tangan Kiri', 'G008', 'Apakah ada nyeri di tangan kiri?'),
(9, 'Nyeri Rahang', 'G009', 'Apakah Anda merasa nyeri di rahang?'),
(10, 'Gangguan Tidur', 'G010', 'Apakah Anda mengalami gangguan tidur?'),
(11, 'Pembengkakan Kaki', 'G011', 'Apakah kaki Anda membengkak?'),
(12, 'Sakit Perut', 'G012', 'Apakah Anda merasakan sakit perut?'),
(13, 'Batuk Kronis', 'G013', 'Apakah Anda mengalami batuk terus-menerus?'),
(14, 'Kelelahan Kronis', 'G014', 'Apakah Anda merasa sangat lelah sepanjang waktu?'),
(15, 'Kehilangan Nafsu Makan', 'G015', 'Apakah Anda kehilangan nafsu makan?'),
(16, 'Kesulitan Berkonsentrasi', 'G016', 'Apakah Anda kesulitan untuk berkonsentrasi?'),
(17, 'Mata Menguning', 'G017', 'Apakah mata Anda terlihat menguning?'),
(18, 'Kulit Pucat', 'G018', 'Apakah kulit Anda tampak pucat?'),
(19, 'Gelisah', 'G019', 'Apakah Anda sering merasa gelisah?'),
(20, 'Nafas Pendek Saat Beraktivitas', 'G020', 'Apakah Anda kesulitan bernapas saat aktivitas ringan?'),
(21, 'Pembengkakan di Perut', 'G021', 'Apakah perut Anda tampak membesar?'),
(22, 'Jantung Berdebar Cepat', 'G022', 'Apakah jantung Anda berdebar cepat?'),
(23, 'Lemas Tanpa Sebab', 'G023', 'Apakah Anda merasa lemas tanpa alasan?'),
(24, 'Kepala Terasa Berat', 'G024', 'Apakah kepala Anda terasa berat?'),
(25, 'Bibir Kebiruan', 'G025', 'Apakah bibir Anda terlihat kebiruan?'),
(26, 'Nyeri Punggung', 'G026', 'Apakah Anda mengalami nyeri punggung?'),
(27, 'Mati Rasa di Lengan', 'G027', 'Apakah lengan Anda sering terasa mati rasa?'),
(28, 'Sakit Kepala Hebat', 'G028', 'Apakah Anda mengalami sakit kepala hebat?'),
(29, 'Pingsan', 'G029', 'Apakah Anda pernah pingsan?'),
(30, 'Sakit Dada Saat Beraktivitas', 'G030', 'Apakah Anda merasakan sakit dada saat beraktivitas?');

INSERT INTO `laporandiagnosis` (`id_laporanDiagnosis`, `id_pengguna`, `id_diagnosis`, `tanggal_diagnosis`, `probabilitas`) VALUES
(1, 2, 1, '2025-05-01', 0.88);
INSERT INTO `laporandiagnosis` (`id_laporanDiagnosis`, `id_pengguna`, `id_diagnosis`, `tanggal_diagnosis`, `probabilitas`) VALUES
(2, 3, 5, '2025-05-02', 0.76);
INSERT INTO `laporandiagnosis` (`id_laporanDiagnosis`, `id_pengguna`, `id_diagnosis`, `tanggal_diagnosis`, `probabilitas`) VALUES
(3, 4, 2, '2025-05-03', 0.91);
INSERT INTO `laporandiagnosis` (`id_laporanDiagnosis`, `id_pengguna`, `id_diagnosis`, `tanggal_diagnosis`, `probabilitas`) VALUES
(4, 5, 3, '2025-05-03', 0.8),
(5, 6, 6, '2025-05-04', 0.7),
(6, 7, 7, '2025-05-05', 0.65),
(7, 8, 8, '2025-05-06', 0.87),
(8, 9, 9, '2025-05-07', 0.89),
(9, 10, 10, '2025-05-08', 0.67),
(10, 11, 11, '2025-05-08', 0.92),
(11, 12, 12, '2025-05-09', 0.73),
(12, 13, 13, '2025-05-09', 0.74),
(13, 14, 14, '2025-05-10', 0.81),
(14, 15, 15, '2025-05-10', 0.83),
(15, 16, 16, '2025-05-11', 0.69),
(16, 17, 17, '2025-05-11', 0.79),
(17, 18, 18, '2025-05-12', 0.85),
(18, 19, 19, '2025-05-12', 0.64),
(19, 20, 20, '2025-05-13', 0.77),
(20, 21, 21, '2025-05-13', 0.86),
(21, 22, 22, '2025-05-14', 0.66),
(22, 23, 23, '2025-05-14', 0.93),
(23, 24, 24, '2025-05-15', 0.71),
(24, 25, 25, '2025-05-15', 0.9),
(25, 26, 26, '2025-05-16', 0.62),
(26, 27, 27, '2025-05-16', 0.8),
(27, 28, 28, '2025-05-17', 0.75),
(28, 29, 29, '2025-05-17', 0.84),
(29, 30, 30, '2025-05-18', 0.78),
(30, 2, 4, '2025-05-18', 0.82);

INSERT INTO `laporangejala` (`id_laporanGejala`, `id_laporanDiagnosis`, `id_gejala`, `value`) VALUES
(1, 1, 1, 1);
INSERT INTO `laporangejala` (`id_laporanGejala`, `id_laporanDiagnosis`, `id_gejala`, `value`) VALUES
(2, 1, 2, 1);
INSERT INTO `laporangejala` (`id_laporanGejala`, `id_laporanDiagnosis`, `id_gejala`, `value`) VALUES
(3, 1, 3, 0);
INSERT INTO `laporangejala` (`id_laporanGejala`, `id_laporanDiagnosis`, `id_gejala`, `value`) VALUES
(4, 2, 4, 1),
(5, 2, 5, 0),
(6, 2, 6, 1),
(7, 3, 7, 1),
(8, 3, 8, 1),
(9, 3, 9, 0),
(10, 4, 10, 1),
(11, 4, 11, 1),
(12, 4, 12, 0),
(13, 5, 13, 1),
(14, 5, 14, 1),
(15, 5, 15, 0),
(16, 6, 16, 1),
(17, 6, 17, 1),
(18, 6, 18, 1),
(19, 7, 19, 0),
(20, 7, 20, 1),
(21, 7, 21, 1),
(22, 8, 22, 1),
(23, 8, 23, 0),
(24, 8, 24, 1),
(25, 9, 25, 1),
(26, 9, 26, 0),
(27, 9, 27, 1),
(28, 10, 28, 1),
(29, 10, 29, 1),
(30, 10, 30, 0);

INSERT INTO `pengguna` (`id_pengguna`, `nama_pengguna`, `email`, `password`, `role`) VALUES
(1, 'Admin', 'admin@email.com', 'admin123', 'admin');
INSERT INTO `pengguna` (`id_pengguna`, `nama_pengguna`, `email`, `password`, `role`) VALUES
(2, 'Budi Santoso', 'budi@gmail.com', 'pass123', 'user');
INSERT INTO `pengguna` (`id_pengguna`, `nama_pengguna`, `email`, `password`, `role`) VALUES
(3, 'Ani Yulia', 'ani@gmail.com', 'pass123', 'user');
INSERT INTO `pengguna` (`id_pengguna`, `nama_pengguna`, `email`, `password`, `role`) VALUES
(4, 'Citra Dewi', 'citra@gmail.com', 'pass123', 'user'),
(5, 'Dedi Kusuma', 'dedi@gmail.com', 'pass123', 'user'),
(6, 'Eka Putri', 'eka@gmail.com', 'pass123', 'user'),
(7, 'Fajar Ramadhan', 'fajar@gmail.com', 'pass123', 'user'),
(8, 'Gina Amelia', 'gina@gmail.com', 'pass123', 'user'),
(9, 'Hari Wibowo', 'hari@gmail.com', 'pass123', 'user'),
(10, 'Intan Maharani', 'intan@gmail.com', 'pass123', 'user'),
(11, 'Joko Widodo', 'joko@gmail.com', 'pass123', 'user'),
(12, 'Kiki Septiani', 'kiki@gmail.com', 'pass123', 'user'),
(13, 'Lukman Hakim', 'lukman@gmail.com', 'pass123', 'user'),
(14, 'Mega Sari', 'mega@gmail.com', 'pass123', 'user'),
(15, 'Nina Pratiwi', 'nina@gmail.com', 'pass123', 'user'),
(16, 'Oscar W', 'oscar@gmail.com', 'pass123', 'user'),
(17, 'Putri M', 'putri@gmail.com', 'pass123', 'user'),
(18, 'Qori Arifin', 'qori@gmail.com', 'pass123', 'user'),
(19, 'Riko Saputra', 'riko@gmail.com', 'pass123', 'user'),
(20, 'Sari Ayu', 'sari@gmail.com', 'pass123', 'user'),
(21, 'Tio Nugroho', 'tio@gmail.com', 'pass123', 'user'),
(22, 'Uci Puspita', 'uci@gmail.com', 'pass123', 'user'),
(23, 'Vina Mardiana', 'vina@gmail.com', 'pass123', 'user'),
(24, 'Wawan Hermawan', 'wawan@gmail.com', 'pass123', 'user'),
(25, 'Xenia Lestari', 'xenia@gmail.com', 'pass123', 'user'),
(26, 'Yusuf Iskandar', 'yusuf@gmail.com', 'pass123', 'user'),
(27, 'Zahra Nuraini', 'zahra@gmail.com', 'pass123', 'user'),
(28, 'Andi Pratama', 'andi@gmail.com', 'pass123', 'user'),
(29, 'Bunga Melati', 'bunga@gmail.com', 'pass123', 'user'),
(30, 'Cahyo Budi', 'cahyo@gmail.com', 'pass123', 'user');


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;