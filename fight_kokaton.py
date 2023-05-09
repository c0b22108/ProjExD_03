import random
import sys
import time
import random
import math

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ

NUM_OF_BOMBS = 5
#def check_bound(area: pg.Rect, obj: pg.Rect) -> tuple[bool, bool]:
def check_bound(area, obj):

    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：オブジェクト（爆弾，こうかとん）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < area.left or area.right < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < area.top or area.bottom < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


class Text:
    """
    イニシャライザには座標を（x,y）の形式で指定してください
    updateでは貼り付けるScreenを引数に取ります。
    set_valueは出力したい文字列を変更したいときに使用します。
    """
    def __init__(self,pos):
        self.font2 = pg.font.SysFont(None, 50)
        self.text2 = self.font2.render(" ", True, (255,0,0))
        self.pos = pos
        self.value = " "
    def update(self,screen):
        screen.blit(self.text2,self.pos)
    
    def set_value(self,value):
        self.value = value
        self.text2 = self.font2.render(self.value, True, (255,0,0))

class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    _delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }
    
    bird_arg = {
        (-1,1):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 45, 2.0),False, False),
        (-1,0):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 0, 2.0),False, False),
        (-1,-1):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), -45, 2.0),False, False),
        (0,-1):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), -90, 2.0),True, False),
        (0,0):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 0, 2.0),True, False),
        (0,1):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 90, 2.0),True, False),
        (1,1):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 45, 2.0),True, False),
        (1,0):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 0, 2.0),True, False),
        (1,-1):pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"fig/3.png"), -45, 2.0),True, False)
        }
    
    
    #def __init__(self, num: int, xy: tuple[int, int]):
    def __init__(self, num: int, xy):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self._img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"fig/{num}.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        self._rct = self._img.get_rect()
        self._rct.center = xy
        self._dv = (0,0)


    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)

    def update(self, key_lst, screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        
        mv_lis = [0,0]
        for k, mv in __class__._delta.items():
            
            if key_lst[k]:
                mv_lis[0] += mv[0]
                mv_lis[1] += mv[1]
                self._rct.move_ip(mv)
                
        if  (tuple(mv_lis) != (0,0)):
            self._img = self.bird_arg[tuple(mv_lis)]
            self._dv = tuple(mv_lis)
        else:
            #self._img = self.bird_arg[tuple(mv_lis)]
            pass
                
    
        if check_bound(screen.get_rect(), self._rct) != (True, True):
            for k, mv in __class__._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
                    
                
        screen.blit(self._img, self._rct)
    
    def get_right(self):
        return self._rct.right
    
    def get_direction(self):
        return self._dv
 



class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color, rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self._img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = +1, +1

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(screen.get_rect(), self._rct)
        if not yoko:
            self._vx *= -1
        if not tate:
            self._vy *= -1
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)
    
    def destroy(self):
        Explosion(self._rct.center)

class Explosion:
    life = 1
    expplode_list = []
    def __init__(self,xy):
        self._img = pg.transform.flip(
                pg.image.load(f"fig/explosion.gif"),
                True, False)
        self._rct = self._img.get_rect()
        self._rct.center = xy
        self._life = time.time()
        self.expplode_list.append(self)
        
    def update(self,screen):
        #print("explode update!")
        if time.time() - self._life < self.life:
            self._img = pg.transform.flip(self._img,True, True)
            screen.blit(self._img, self._rct)
            #print("explode blited")
        else:
            #print("removed")
            __class__.expplode_list.remove(self)
            
class Beam:
    def __init__(self, bird_obj):
        self._img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"fig/beam.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        
        self._rct = self._img.get_rect()
        self._rct.center = bird_obj._rct.center
        self._vx, self._vy = bird_obj.get_direction()  
        
        self._rct.center = (self._rct.center[0] + self._vx * abs(bird_obj._rct.center[0]-bird_obj._rct.right),
                            self._rct.center[1] + self._vy * abs(bird_obj._rct.center[0]-bird_obj._rct.right))
        
        
        self._img = pg.transform.rotozoom(
                pg.image.load(f"fig/beam.png"), 
                math.degrees(math.atan2(-self._vy,self._vx)), 
                1.0)
    def update(self, screen: pg.Surface):
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)
    
    def destroy(self):
        Explosion(self._rct.center)
        
    
 
def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")

    bird = Bird(3, (900, 400))
    
    bombs = []
    for i in range(NUM_OF_BOMBS):
        bombs.append(  Bomb( (random.randint(0,255), random.randint(0,255), random.randint(0,255) ,random.randint(0,255)), (random.randint(8,20)) ))

    tmr = 0
    
    score_value = 0
    
    beams = []
    finish_flg = False
    
    final_fire_time = time.time()
    
    score = Text((200,200))
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        tmr += 1
        screen.blit(bg_img, [0, 0])
        
        
        
        
        if finish_flg:
            bird.change_img(6, screen)
            pg.display.update()
            time.sleep(1)
            
            return         
        
        for bomb in bombs:
            if bird._rct.colliderect(bomb._rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return

        key_lst = pg.key.get_pressed()
        if key_lst[pg.K_SPACE]:
            if  time.time() - final_fire_time > 1:
                final_fire_time = time.time()
                beams.append(Beam(bird))
        
        #multibream
        pop_index = 0
        for i,beam in enumerate(beams):
            beam.update(screen)
            for j,bomb in enumerate(bombs):
                if bombs != []:
                    if beam._rct.colliderect(bomb._rct):
                        beam.destroy()
                        bomb.destroy()
                        beams.pop(i - pop_index)
                        bombs.pop(j - pop_index)
                        pop_index += 1
                        score_value += 100
                        score.set_value(f"score : {score_value}")
                        
        #print(len(Explosion.expplode_list))
        for explode in Explosion.expplode_list:
            explode.update(screen)
                        
        score.update(screen)
        
        bird.update(key_lst, screen)
        if bombs != []:
            for bomb in bombs:
                bomb.update(screen)
        pg.display.update()
        clock.tick(1000)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
