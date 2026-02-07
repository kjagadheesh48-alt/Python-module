class vechicle{
    protected int speed;   
}
class bike extends vechicle{
    void setspeed(int s){
        speed=s;
    }
    int getSpeed(){
        return speed;
    }
}
public class main1h{
    public static void main(String[] args){
        bike b = new bike();
        b.setspeed(100);
        System.out.println("Access via subclass:"+b.getSpeed());
        vechicle v = new vechicle();
        System.out.println(v.speed);
    }


}
