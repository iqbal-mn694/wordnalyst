const kataGaulSelect = document.getElementById('kataGaul');
const prediksiValue = document.getElementById('prediksiValue');
const tanggalInput = document.getElementById('tanggalPrediksi');
const prediksiOutput = document.getElementById('prediksiOutput');

const dummyPrediksi = {
  anjay: 70,
  gaskeun: 55,
  mager: 80,
  santuy: 60
};

function getHariTanggal(dateStr) {
  if (!dateStr) return { hari: '...', tanggal: '...' };
  const hariArr = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
  const d = new Date(dateStr);
  const hari = hariArr[d.getDay()];
  const tgl = d.getDate().toString().padStart(2, '0');
  const bln = (d.getMonth() + 1).toString().padStart(2, '0');
  const thn = d.getFullYear();
  return { hari, tanggal: `${tgl}-${bln}-${thn}` };
}

function updatePrediksi() {
  const kata = kataGaulSelect.value;
  const tgl = tanggalInput.value;
  const prediksi = dummyPrediksi[kata] || 70;
  const hariTanggal = getHariTanggal(tgl);
  let hasil = '...';
  if (tgl) hasil = prediksi;
  prediksiOutput.innerHTML = `Prediksi popularitas kata <b>"${kata}"</b> pada hari <b>${hariTanggal.hari}</b>, tanggal <b>${hariTanggal.tanggal}</b> adalah <span id=\"prediksiValue\">${hasil}</span>`;
}

if (kataGaulSelect && prediksiValue && tanggalInput && prediksiOutput) {
  kataGaulSelect.addEventListener('change', updatePrediksi);
  tanggalInput.addEventListener('change', updatePrediksi);
}

updatePrediksi();

const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');

if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    if (mobileMenu.classList.contains('hidden')) {
      mobileMenu.classList.remove('hidden');
      hamburger.classList.add('active');
    } else {
      mobileMenu.style.animation = 'slideUp 0.3s ease-in-out';
      hamburger.classList.remove('active');
      setTimeout(() => {
        mobileMenu.classList.add('hidden');
        mobileMenu.style.animation = '';
      }, 300);
    }
  });
}

function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (!section) return;
  
  const navbarHeight = document.querySelector('nav').offsetHeight;
  const sectionPosition = section.getBoundingClientRect().top;
  const offsetPosition = sectionPosition + window.pageYOffset - navbarHeight;

  window.scrollTo({
    top: offsetPosition,
    behavior: 'smooth'
  });
}
document.querySelectorAll('nav a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const sectionId = link.getAttribute('href').substring(1);
    scrollToSection(sectionId);

    if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
      mobileMenu.style.animation = 'slideUp 0.3s ease-in-out';
      hamburger.classList.remove('active');
      setTimeout(() => {
        mobileMenu.classList.add('hidden');
        mobileMenu.style.animation = '';
      }, 300);
    }
  });
});
