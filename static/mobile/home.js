$(document).ready(function(){
            $('.owl-carousel').owlCarousel({
                loop: true,
                margin: 10,
                nav: true,
                navText: [
                    '<span class="material-symbols-outlined">arrow_back_ios</span>',
                    '<span class="material-symbols-outlined">arrow_forward_ios</span>'
                ],
                responsive: {
                    0: {
                        items: 2.5
                    },
                    600: {
                        items: 2.5
                    },
                    1000: {
                        items: 5
                    }
                }
            });

            document.querySelectorAll('.nav-link').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.nav-link').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('show', 'active'));
                    document.querySelector(this.getAttribute('data-bs-target')).classList.add('show', 'active');
                });
            });
        });