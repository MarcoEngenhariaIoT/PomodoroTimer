"""
Aplicativo Pomodoro Timer

Aplicativo usado para auxiliar nos estudos usando a técnica pomodoro. 
Esse projeto é de uso livre com bibliotecas free, 
pode ser copiado e usado livremente desde que seja citado minha autoria.

Engenheiro Marco Aurélio Machado
Versão 1.0.0
19/09/2025
marcoengenhariaiot@gmail.com

"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import threading
import winsound  # Para Windows
import webbrowser
import urllib.parse

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Configurações padrão
        self.study_time = 25 * 60  # 25 minutos em segundos
        self.short_break = 5 * 60  # 5 minutos em segundos
        self.long_break = 15 * 60  # 15 minutos em segundos
        self.cycles = 4  # Número de ciclos antes do descanso longo
        
        # Variáveis de estado
        self.current_time = self.study_time
        self.current_cycle = 0
        self.is_running = False
        self.is_paused = False
        self.is_study_time = True
        self.timer_thread = None
        
        # Configurar a interface
        self.setup_ui()
        
        # Atualizar o display inicial
        self.update_display()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Pomodoro Timer", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # Display do tempo
        self.time_display = ttk.Label(main_frame, text="25:00", font=("Arial", 48, "bold"))
        self.time_display.grid(row=1, column=0, columnspan=3, pady=20)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Pronto para começar", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Iniciar", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.pause_button = ttk.Button(button_frame, text="Pausar", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="Parar", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=10)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Informações do ciclo
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Ciclo", padding="10")
        info_frame.grid(row=5, column=0, columnspan=3, pady=20, sticky=(tk.W, tk.E))
        
        self.cycle_label = ttk.Label(info_frame, text="Ciclo atual: 0/4")
        self.cycle_label.grid(row=0, column=0, sticky=tk.W)
        
        self.mode_label = ttk.Label(info_frame, text="Modo: Estudo")
        self.mode_label.grid(row=1, column=0, sticky=tk.W)
        
        # Menu
        self.setup_menu()
        
        # Configurar peso das linhas e colunas para expansão
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Configurações
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=config_menu)
        config_menu.add_command(label="Preferências", command=self.open_config)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.open_about)
    
    def beep(self):
        # Frequência e duração do som (Windows)
        try:
            winsound.Beep(1000, 500)  # 1000 Hz por 0.5 segundos
        except:
            # Fallback para sistemas sem winsound
            print("\a")  # Emite um alerta sonoro do sistema
    
    def update_timer(self):
        while self.is_running and not self.is_paused and self.current_time > 0:
            time.sleep(1)
            if self.is_running and not self.is_paused:
                self.current_time -= 1
                self.update_display()
        
        if self.current_time <= 0 and self.is_running:
            self.root.after(0, self.timer_finished)
    
    def timer_finished(self):
        self.beep()
        
        if self.is_study_time:
            self.current_cycle += 1
            
            if self.current_cycle >= self.cycles:
                # Hora do descanso longo
                self.status_label.config(text="Descanso longo de 15 minutos!")
                self.current_time = self.long_break
                self.current_cycle = 0  # Reiniciar contador de ciclos
            else:
                # Hora do descanso curto
                self.status_label.config(text="Descanso curto de 5 minutos!")
                self.current_time = self.short_break
            
            self.is_study_time = False
            self.mode_label.config(text="Modo: Descanso")
        else:
            # Voltar ao estudo
            self.status_label.config(text="Hora de estudar!")
            self.current_time = self.study_time
            self.is_study_time = True
            self.mode_label.config(text="Modo: Estudo")
        
        self.update_display()
        
        # Se o timer ainda estiver rodando, iniciar o próximo ciclo
        if self.is_running:
            self.timer_thread = threading.Thread(target=self.update_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def update_display(self):
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.time_display.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Atualizar barra de progresso
        total_time = self.study_time if self.is_study_time else (self.short_break if self.current_cycle < self.cycles else self.long_break)
        progress_value = ((total_time - self.current_time) / total_time) * 100
        self.progress['value'] = progress_value
        
        # Atualizar informações do ciclo
        self.cycle_label.config(text=f"Ciclo atual: {self.current_cycle}/{self.cycles}")
    
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            
            if self.current_time == self.study_time and not self.is_study_time:
                self.status_label.config(text="Hora de estudar!")
            elif not self.is_study_time:
                if self.current_time == self.short_break:
                    self.status_label.config(text="Descanso curto de 5 minutos!")
                else:
                    self.status_label.config(text="Descanso longo de 15 minutos!")
            else:
                self.status_label.config(text="Hora de estudar!")
            
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            
            self.timer_thread = threading.Thread(target=self.update_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def pause_timer(self):
        if self.is_running:
            if self.is_paused:
                self.is_paused = False
                self.status_label.config(text=self.status_label.cget("text").replace("(Pausado) ", ""))
                self.pause_button.config(text="Pausar")
                
                self.timer_thread = threading.Thread(target=self.update_timer)
                self.timer_thread.daemon = True
                self.timer_thread.start()
            else:
                self.is_paused = True
                self.status_label.config(text="(Pausado) " + self.status_label.cget("text"))
                self.pause_button.config(text="Continuar")
    
    def stop_timer(self):
        self.is_running = False
        self.is_paused = False
        
        self.reset_timer()
        
        self.status_label.config(text="Pronto para começar")
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(text="Pausar")
    
    def reset_timer(self):
        self.current_time = self.study_time
        self.current_cycle = 0
        self.is_study_time = True
        self.mode_label.config(text="Modo: Estudo")
        self.update_display()
    
    def open_config(self):
        # Criar uma janela de diálogo para configurações
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurações")
        config_window.geometry("400x300")
        config_window.resizable(False, False)
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(config_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Campos de configuração
        ttk.Label(main_frame, text="Tempo de estudo (minutos):").grid(row=0, column=0, sticky=tk.W, pady=10)
        study_spin = ttk.Spinbox(main_frame, from_=1, to=60, width=10)
        study_spin.grid(row=0, column=1, sticky=tk.E, pady=10)
        study_spin.set(self.study_time // 60)
        
        ttk.Label(main_frame, text="Descanso curto (minutos):").grid(row=1, column=0, sticky=tk.W, pady=10)
        short_spin = ttk.Spinbox(main_frame, from_=1, to=30, width=10)
        short_spin.grid(row=1, column=1, sticky=tk.E, pady=10)
        short_spin.set(self.short_break // 60)
        
        ttk.Label(main_frame, text="Descanso longo (minutos):").grid(row=2, column=0, sticky=tk.W, pady=10)
        long_spin = ttk.Spinbox(main_frame, from_=1, to=60, width=10)
        long_spin.grid(row=2, column=1, sticky=tk.E, pady=10)
        long_spin.set(self.long_break // 60)
        
        ttk.Label(main_frame, text="Ciclos até descanso longo:").grid(row=3, column=0, sticky=tk.W, pady=10)
        cycles_spin = ttk.Spinbox(main_frame, from_=1, to=10, width=10)
        cycles_spin.grid(row=3, column=1, sticky=tk.E, pady=10)
        cycles_spin.set(self.cycles)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save_config():
            try:
                self.study_time = int(study_spin.get()) * 60
                self.short_break = int(short_spin.get()) * 60
                self.long_break = int(long_spin.get()) * 60
                self.cycles = int(cycles_spin.get())
                
                # Reiniciar com os novos valores se não estiver executando
                if not self.is_running:
                    self.reset_timer()
                
                config_window.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira valores válidos.")
        
        ttk.Button(button_frame, text="Salvar", command=save_config).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Cancelar", command=config_window.destroy).grid(row=0, column=1, padx=10)
        
        # Configurar peso das linhas e colunas para expansão
        config_window.columnconfigure(0, weight=1)
        config_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def open_about(self):
        # Criar uma janela personalizada para o diálogo "Sobre"
        about_window = tk.Toplevel(self.root)
        about_window.title("Sobre")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.configure(bg='#f0f0f0')
        
        # Frame principal
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Pomodoro Timer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)
        
        # Texto descritivo
        desc_text = (
            "Um aplicativo para gerenciar sua técnica Pomodoro de estudo.\n\n"
            "Versão: 1.0.0\n"
            "Desenvolvedor: Engenheiro Marco Aurélio Machado\n\n"
            "Técnica Pomodoro:\n"
            "1. Escolha uma tarefa para realizar\n"
            "2. Estude por 25 minutos\n"
            "3. Faça uma pausa curta de 5 minutos\n"
            "4. A cada 4 ciclos, faça uma pausa longa de 15 minutos"
        )
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.grid(row=1, column=0, sticky=tk.W, pady=10)
        
        # E-mail clicável
        email_frame = ttk.Frame(main_frame)
        email_frame.grid(row=2, column=0, pady=10, sticky=tk.W)
        
        ttk.Label(email_frame, text="E-mail: ").grid(row=0, column=0, sticky=tk.W)
        
        # Criar um label que parece um link
        email_label = ttk.Label(email_frame, text="marcoengenhariaiot@gmail.com", 
                            foreground="blue", cursor="hand2")
        email_label.grid(row=0, column=1, sticky=tk.W)
        
        # Tornar o label clicável
        email_label.bind("<Button-1>", lambda e: self.send_email())
        
        # Botão Fechar
        ttk.Button(main_frame, text="Fechar", command=about_window.destroy).grid(row=3, column=0, pady=20)
        
        # Configurar peso das linhas e colunas para expansão
        about_window.columnconfigure(0, weight=1)
        about_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def send_email(self):
        # Abrir o cliente de e-mail padrão com o endereço preenchido

        
        email = "marcoengenhariaiot@gmail.com"
        subject = "Contato sobre o Pomodoro Timer"
        body = "Olá, gostaria de entrar em contato sobre o aplicativo Pomodoro Timer."
        
        # Criar o link mailto
        mailto_link = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        
        # Abrir o cliente de e-mail
        webbrowser.open(mailto_link)

def main():
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()