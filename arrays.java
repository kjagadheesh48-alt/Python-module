public class arrays{
    public static void main(String[] args){
        int[] arr= {10,20,30,40,50};
        int n=  arr.length;
        System.out.println("Primitive Arrays:");
        for(int i=0;i<n;i++){
            System.out.println(arr[i]+" ");
        System.out.println();
        }
        String[] names={"Lakshit", "Rahul", "Pankaj"};
        System.out.println("non-primitive Arrays:");
        for(int i=0;i<names.length;i++){
        System.out.println(names[i]+" ");
    }
    }
}
        